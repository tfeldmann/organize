import collections
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Any, DefaultDict, Dict, Mapping, Optional, Union

import exifread

from .filter import Filter, FilterResult

ExifDict = Mapping[str, Union[str, Mapping[str, str]]]

def to_datetime(key: str, value: str) -> Union[datetime, date, timezone, str]:
    """Converts exif datetime/date/offsettime fields to datetime objects

    :returns:
        ``value`` -- converted to datetime, date or timezone if possible

        - ``{datetime.datetime}`` -- If `key` contains "datetime" 
                                     (e.g. image.datetime, exif.datetimeoriginal, exif.datetimedigitized)
        - ``{datetime.date}``     -- If `key` contains "date" 
                                     (e.g. gps.date)
        - ``{datetime.timezone}`` -- If `key` contains "offsettime" 
                                     (e.g. exif.offsettimeoriginal, exif.offsettimedigitized)
    """

    if "datetime" in key:
        # value = "YYYY:MM:DD HH:MM:SS" --> convert to 'datetime.datetime'
        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    elif "date" in key:
        # value = "YYYY:MM:DD" --> convert to datetime.date
        return datetime.strptime(value, "%Y:%m:%d").date()
    elif "offsettime" in key:
        # value = "+HH:MM" or "UTC+HH:MM" --> convert to 'datetime.timezone'
        if value[:3].upper() == "UTC":
            value = value[3:]
        return datetime.strptime(value, "%z").tzinfo
    return value

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

    name = "exif"
    arg_schema = None
    schema_support_instance_without_args = True

    def __init__(self, *required_tags: str, **tag_filters: str) -> None:
        self.args = required_tags  # expected exif keys
        self.kwargs = tag_filters  # exif keys with expected values

    def category_dict(self, tags: Mapping[str, str]) -> ExifDict:
        result = collections.defaultdict(dict)  # type: DefaultDict
        for key, value in tags.items():
            if " " in key:
                category, field = key.split(" ", maxsplit=1)
                result[category][field] = to_datetime(field, value)
            else:
                result[key] = to_datetime(key, value)
        return dict(result)

    def matches(self, exiftags: dict) -> bool:
        if not exiftags:
            return False
        tags = {k.lower(): v for k, v in exiftags.items()}

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
            updates={self.get_name(): exif_result},
        )

    def __str__(self) -> str:
        return "EXIF(%s)" % ", ".join("%s=%s" % (k, v) for k, v in self.kwargs.items())
