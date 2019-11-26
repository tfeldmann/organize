import collections
from typing import Any, DefaultDict, Dict, Mapping, Optional, Union

import exifread  # type: ignore

from organize.compat import Path

from .filter import Filter

ExifDict = Mapping[str, Union[str, Mapping[str, str]]]


class Exif(Filter):

    """
    Filter by image EXIF data

    The `exif` filter can be used as a filter as well as a way to get exif information
    into your actions.

    :returns:
        ``{exif}`` -- a dict of all the collected exif inforamtion available in the
        file. Typically it consists of the following tags (if present in the file):

        - ``{exif.image}`` -- information related to the main image
        - ``{exif.exif}`` -- Exif information
        - ``{exif.gps}`` -- GPS information
        - ``{exif.interoperability}`` -- Interoperability information

    Examples:
        - Show available EXIF data of your pictures:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Pictures
                subfolders: true
                filters:
                  - exif
                actions:
                  - echo: "{exif}"

        - Copy all images which contain GPS information while keeping subfolder
          structure:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
            - folders: ~/Pictures
              subfolders: true
              filters:
                - exif:
                    gps.gpsdate
              actions:
                - copy: ~/Pictures/with_gps/{relative_path}/

        - Filter by camera manufacturer:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Pictures
                subfolders: true
                filters:
                  - exif:
                      image.model: Nikon D3200
                actions:
                  - move: '~/Pictures/My old Nikon/'

        - Sort images by camera manufacturer. This will create folders for each camera
          model (for example "Nikon D3200", "iPhone 6s", "iPhone 5s", "DMC-GX80") and
          move the pictures accordingly:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Pictures
                subfolders: true
                filters:
                  - extension: jpg
                  - exif:
                      image.model
                actions:
                  - move: '~/Pictures/{exif.image.model}/'
    """

    def __init__(self, *required_tags: str, **tag_filters: str) -> None:
        self.args = required_tags  # expected exif keys
        self.kwargs = tag_filters  # exif keys with expected values

    def category_dict(self, tags: Mapping[str, str]) -> ExifDict:
        result = collections.defaultdict(dict)  # type: DefaultDict[str, Dict[str, str]]
        for key, value in tags.items():
            if " " in key:
                category, field = key.split(" ", maxsplit=1)
                result[category][field] = value
            else:
                result[key] = value  # type: ignore
        return result

    def matches(self, path: Path) -> Union[bool, ExifDict]:
        # NOTE: This should return Union[Literal[False], ExifDict] but Literal is only
        # available in Python>=3.8.
        with path.open("rb") as f:
            exiftags = exifread.process_file(f, details=False)  # type: Dict
        if not exiftags:
            return False

        tags = {k.lower(): v.printable for k, v in exiftags.items()}

        # no match if expected tag is not found
        normkey = lambda k: k.replace(".", " ").lower()
        for key in self.args:
            if normkey(key) not in tags:
                return False
        # no match if tag has not expected value
        for key, value in self.kwargs.items():
            key = normkey(key)
            if not (key in tags and tags[key].lower() == value.lower()):
                return False
        return self.category_dict(tags)

    def pipeline(self, args: Mapping[str, Any]) -> Optional[Dict[str, ExifDict]]:
        tags = self.matches(args["path"])
        if isinstance(tags, dict):
            return {"exif": tags}
        return None

    def __str__(self) -> str:
        return "EXIF(%s)" % ", ".join("%s=%s" % (k, v) for k, v in self.kwargs.items())
