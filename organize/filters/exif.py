import collections
import fnmatch
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import ClassVar, Dict, Optional, Union

import exifread
import simplematch as sm
from pydantic import BaseModel
from rich import print

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource

ExifValue = Union[str, datetime, date, timedelta]
ExifDict = Dict[str, Union[ExifValue, Dict[str, ExifValue]]]


def parse_tag(key: str, value: str) -> ExifValue:
    """
    Try to parse `value` for the given `key`.

    - If `key` contains "datetime" convert `value` to 'datetime.datetime'
        (e.g. image.datetime, exif.datetimeoriginal, exif.datetimedigitized)
    - If `key` contains "date" convert `value` to 'datetime.date'
        (e.g. gps.date)
    - If `key` contains "offsettime" convert `value` to 'datetime.timedelta'
        (e.g. exif.offsettimeoriginal, exif.offsettimedigitized)
    - Otherwise `value` is not converted and returned as is
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


def parse_and_categorize(tags: Dict[str, str]) -> ExifDict:
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


def matches_tags(filter_tags: Dict[str, Optional[str]], data: ExifDict) -> bool:
    if not data:
        return False
    for k, v in filter_tags.items():
        try:
            # step into the data dict by dotted notation
            data_value = data
            for part in k.split("."):
                data_value = data_value[part]
            # if v is None it's enough for the key to exist in the data.
            # Otherwise we use a glob matcher to check for matches
            if v is not None and not fnmatch.fnmatch(data_value.lower(), v.lower()):
                return False
        except KeyError:
            return False
    return True


class Exif(BaseModel):
    """Filter by image EXIF data

    The `exif` filter can be used as a filter as well as a way to get exif information
    into your actions.

    Exif fields which contain "datetime", "date" or "offsettime" in their fieldname
    will have their value converted to 'datetime.datetime', 'datetime.date' and
    'datetime.timedelta' respectivly.
    - `datetime.datetime` : exif.image.datetime, exif.exif.datetimeoriginal, ...
    - `datetime.date` : exif.gps.date, ...
    - `datetime.timedelta` : exif.exif.offsettimeoriginal, exif.exif.offsettimedigitized, ...

    :returns:
        ``{exif}`` -- a dict of all the collected exif inforamtion available in the
        file. Typically it consists of the following tags (if present in the file):

        - ``{exif.image}`` -- information related to the main image
        - ``{exif.exif}`` -- Exif information
        - ``{exif.gps}`` -- GPS information
        - ``{exif.interoperability}`` -- Interoperability information
    """

    filter_tags: Dict

    filter_config: ClassVar = FilterConfig(
        name="exif",
        files=True,
        dirs=False,
    )

    def __init__(self, *args, filter_tags: Optional[Dict] = None, **kwargs):
        # exif filter is used differently from other filters. The **kwargs are not
        # filter parameters but all belong into the filter_tags dicttionary to filter
        # for specific exif tags.
        # *args are tags filtered without a value, like ["gps", "image.model"].
        params = filter_tags or dict()
        params.update(kwargs)
        for arg in args:
            params[arg] = None
        super().__init__(filter_tags=params)

    def pipeline(self, res: Resource, output: Output) -> bool:
        data = read_exif_data(res.path)
        parsed = parse_and_categorize(data)
        res.vars[self.filter_config.name] = parsed
        return matches_tags(self.filter_tags, parsed)


if __name__ == "__main__":
    import sys

    # Usage:
    # python organize/filters/exif.py tests/resources/images-with-exif/3.jpg
    data = read_exif_data(Path(sys.argv[1]))
    parsed = parse_and_categorize(data)
    print(data)
    print(parsed)
