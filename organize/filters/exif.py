import collections
from typing import Any, DefaultDict, Dict, Mapping, Union

import exifread
import simplematch as sm
from pydantic import Field, root_validator
from typing_extensions import Literal

from .filter import Filter, FilterResult

ExifDict = Mapping[str, Union[str, Mapping[str, str]]]


class Exif(Filter):
    """Filter by image EXIF data

    The `exif` filter can be used as a filter as well as a way to get exif information
    into your actions.

    :returns:
        ``{exif}`` -- a dict of all the collected exif inforamtion available in the
        file. Typically it consists of the following tags (if present in the file):

        - ``{exif.image}`` -- information related to the main image
        - ``{exif.exif}`` -- Exif information
        - ``{exif.gps}`` -- GPS information
        - ``{exif.interoperability}`` -- Interoperability information
    """

    name: Literal["exif"] = Field("exif", repr=False)
    tags: Dict[str, Any]

    class Config:
        extra = "allow"

    @root_validator(pre=True)
    def build_extra(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # assemble all given extra kwargs into the self.tags dict
        extra: Dict[str, Any] = {}
        for field_name in list(values):
            if field_name != "name":
                extra[field_name] = values.pop(field_name)
        values["tags"] = extra
        return values

    def category_dict(self, tags: Mapping[str, str]) -> ExifDict:
        result = collections.defaultdict(dict)  # type: DefaultDict
        for key, value in tags.items():
            if " " in key:
                category, field = key.split(" ", maxsplit=1)
                result[category][field] = value
            else:
                result[key] = value
        return dict(result)

    def matches(self, exiftags: dict) -> bool:
        if not exiftags:
            return False
        tags = {k.lower(): v for k, v in exiftags.items()}

        # no match if tag has not expected value
        normkey = lambda k: k.replace(".", " ").lower()
        for key, value in self.tags.items():
            key = normkey(key)
            if not (key in tags and sm.match(value.lower(), tags[key].lower())):
                return False
        return True

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]
        fs_path = args["fs_path"]
        with fs.openbin(fs_path) as f:
            exiftags = exifread.process_file(f, details=False)

        tags = {k.lower(): v.printable for k, v in exiftags.items()}
        matches = self.matches(tags)
        exif_result = self.category_dict(tags)

        return FilterResult(
            matches=matches,
            updates={self.name: exif_result},
        )
