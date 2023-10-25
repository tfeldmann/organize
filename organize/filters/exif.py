import collections
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import ClassVar, Dict, Union

import exifread
import simplematch as sm
from pydantic import BaseModel, PrivateAttr
from rich import print

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource

ExifValue = Union[str, datetime, date, timedelta]


def parse_tag(key: str, value: str) -> ExifValue:
    """
    Try to parse `value` for the given `key`.
    """
    _key = key.lower()
    try:
        if "datetime" in _key:
            # value = "YYYY:MM:DD HH:MM:SS"
            return datetime.strptime(value[:19], "%Y:%m:%d %H:%M:%S")
        elif "date" in _key:
            # value = "YYYY:MM:DD"
            return datetime.strptime(value[:10], "%Y:%m:%d").date()
        elif "offsettime" in _key:
            # value = "+HHMM" or "+HH:MM[:SS]" or "UTC+HH:MM[:SS]"
            if value[:3].upper() == "UTC":
                # Remove UTC
                value = value[3:]
            return datetime.strptime(
                value.replace(":", ""), "%z"
            ).utcoffset() or timedelta(seconds=0)
        return value
    except Exception:
        return value


def parse_and_categorize(
    tags: Dict[str, str]
) -> Dict[str, Union[ExifValue, Dict[str, ExifValue]]]:
    result = collections.defaultdict(dict)
    for key, value in tags.items():
        if " " in key:
            category, field = key.split(" ", maxsplit=1)
            result[category][field] = parse_tag(key=field, value=value)
        else:
            result[key] = parse_tag(key=key, value=value)
    return dict(result)


def read_exif_data(path: Path) -> Dict[str, str]:
    """
    returns parsed and categorized exif data for the given path.
    """
    data = exifread.process_file(fh=path.open("rb"), details=False, debug=False)
    printable = {key.lower(): val.printable for (key, val) in data.items()}
    return printable


class Exif(BaseModel):
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

    filter_config: ClassVar = FilterConfig(
        name="exif",
        files=True,
        dirs=False,
    )
    _filter_tags: Dict = PrivateAttr(default_factory=dict)

    def __init__(self, **data):
        super().__init__()
        self._filter_tags = data

    # def matches(self, exiftags: dict) -> bool:
    #     if not exiftags:
    #         return False
    #     tags = {k.lower(): v for k, v in exiftags.items()}

    #     # no match if tag has not expected value
    #     normkey = lambda k: k.replace(".", " ").lower()
    #     for key, value in self.tags.items():
    #         key = normkey(key)
    #         if not (key in tags and sm.match(value.lower(), tags[key].lower())):
    #             return False
    #     return True

    def matches(self, data):
        if not self._filter_tags:
            return True
        if not data:
            return False
        for key, val in self._filter_tags.items():
            # TODO not working!!
            nkey = key.replace(".", " ").lower()
            if not (
                key in self._filter_tags and sm.match(val.lower(), data[nkey].lower())
            ):
                return False
        return True

    def pipeline(self, res: Resource, output: Output) -> bool:
        data = read_exif_data(res.path)
        parsed = parse_and_categorize(data)
        res.vars[self.filter_config.name] = parsed
        return self.matches(data)


if __name__ == "__main__":
    import sys

    # Usage:
    # python organize/filters/exif.py tests/resources/images-with-exif/3.jpg
    data = read_exif_data(Path(sys.argv[1]))
    parsed = parse_and_categorize(data)
    print(data)
    print(parsed)
