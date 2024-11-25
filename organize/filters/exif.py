import collections
import fnmatch
import json
import os
import subprocess
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, ClassVar, DefaultDict, Dict, Optional, Union

import exifread
from pydantic import BaseModel
from rich import print

from organize.filter import FilterConfig
from organize.logger import logger
from organize.output import Output
from organize.resource import Resource

ExifStrDict = Dict[str, Dict[str, str]]
ExifValue = Union[str, datetime, date, timedelta]
ExifDict = Dict[str, Dict[str, ExifValue]]
ExifDefaultDict = DefaultDict[str, DefaultDict[str, ExifValue]]

ORGANIZE_EXIFTOOL_PATH = os.environ.get("ORGANIZE_EXIFTOOL_PATH", "")


@lru_cache(maxsize=1)
def exiftool_available() -> bool:
    # don't use exiftool if user blanked the env path
    if not ORGANIZE_EXIFTOOL_PATH:
        return False

    # check whether the given path is executable
    try:
        subprocess.check_call(
            [ORGANIZE_EXIFTOOL_PATH, "-ver"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        return True
    except subprocess.CalledProcessError:
        logger.warning("exiftool not available. Falling back to exifread library.")
        return False


def group_keys_by_splitting(
    data: Dict[str, Any],
    delimiter: str = " ",
) -> Dict[str, Dict[str, Any]]:
    """
    >>> group_keys_by_splitting({"cat a": 1, "cat b": 2, "x c": 1, "x d": 2})
    {"cat": {"a": 1, "b": 2}, "x": {"c": 1, "d": 2}}
    """
    result: DefaultDict[str, Any] = collections.defaultdict(dict)
    for k, v in data.items():
        if delimiter in k:
            category, field = k.split(delimiter, maxsplit=1)
            result[category][field] = v
        else:
            result[k] = v
    return dict(result)


def lowercase_keys_recursive(data) -> Dict:
    if isinstance(data, Dict):
        return {k.lower(): lowercase_keys_recursive(v) for k, v in data.items()}
    return data


def parse_date_value(value: str) -> Union[datetime, date, str]:
    """
    Parse datetime or date values (e.g. image.datetime, exif.datetimeoriginal, ...)
    Exiftool often gives date and time values for keys with only "date" in their name
    so we have to check both in order to preserve this information.
    """
    try:
        return datetime.strptime(value[:19], "%Y:%m:%d %H:%M:%S")
    except ValueError:
        pass
    try:
        return datetime.strptime(value[:10], "%Y:%m:%d").date()
    except ValueError:
        pass
    return value


def parse_offset_value(value: str) -> Union[timedelta, str]:
    """
    Parse offset values (e.g. exif.offsettimeoriginal, exif.offsettimedigitized)
    Supports formats "+HHMM" or "+HH:MM[:SS]" or "UTC+HH:MM[:SS]"
    """
    try:
        if value[:3].upper() == "UTC":
            value = value[3:]  # remove UTC
        return datetime.strptime(value.replace(":", ""), "%z").utcoffset() or timedelta(
            seconds=0
        )
    except (ValueError, TypeError):
        return value


def convert_value(key: str, value: str) -> ExifValue:
    _key = key.lower()
    if "date" in _key:
        return parse_date_value(value)
    if "offset" in _key:
        return parse_offset_value(value)
    return value


def convert_recursive(data):
    result = dict()
    for k, v in data.items():
        if isinstance(v, Dict):
            result[k] = convert_recursive(v)
        else:
            result[k] = convert_value(k, v)
    return result


def exifread_read(path: Path) -> ExifStrDict:
    """
    Uses the `exifread` library to read the EXIF data
    """
    with path.open("rb") as f:
        data = exifread.process_file(fh=f, details=False, debug=False)
    # at this point data still contains exifread specific types like
    # Short / Ratio / ASCII which we now convert to a printable representation
    printable = {key: val.printable for (key, val) in data.items()}
    grouped = group_keys_by_splitting(printable)
    return grouped


def exiftool_read(path: Path) -> ExifStrDict:
    """
    Uses the `exiftool` tool by Phil Harvey to read the EXIF data
    """
    try:
        data_json = subprocess.check_output(
            (
                ORGANIZE_EXIFTOOL_PATH,
                "-j",
                "-g",
                "--fast",
                str(path),
            ),
            text=True,
        )
    except subprocess.CalledProcessError:
        return dict()

    # we pass a single filepath, so we are interested in the first element
    data: Dict = json.loads(data_json)[0]

    # if the result only contains "File", "SourceFile" and "ExifTool" it means exiftool
    # couldn't find any additional data about this file.
    if set(data.keys()) == set(["SourceFile", "ExifTool", "File"]):
        return dict()

    return data


def matches_tags(
    filter_tags: Dict[str, Optional[str]],
    data: Dict[str, Dict[str, str]],
) -> bool:
    if not data:
        return False
    for k, v in filter_tags.items():
        try:
            # step into the data dict by dotted notation
            data_value: Any = data
            for part in k.split("."):
                data_value = data_value[part]
            # if v is None it's enough for the key to exist in the data.
            # Otherwise we use a glob matcher to check for matches
            if v is not None and not fnmatch.fnmatch(data_value.lower(), v.lower()):
                return False
        except (KeyError, AttributeError):
            return False
    return True


class Exif(BaseModel):
    """Filter by image EXIF data

    The `exif` filter can be used as a filter as well as a way to get exif information
    into your actions.

    By default this library uses the `exifread` library. If your image format is not
    supported you can install `exiftool` (exiftool.org) and set the environment variable:

    ```
    ORGANIZE_EXIFTOOL_PATH="exiftool"
    ```

    organize will then use `exiftool` to extract the EXIF data.

    Exif fields which contain "datetime", "date" or "offsettime" in their fieldname
    will have their value converted to 'datetime.datetime', 'datetime.date' and
    'datetime.timedelta' respectivly.
    - `datetime.datetime` : exif.image.datetime, exif.exif.datetimeoriginal, ...
    - `datetime.date` : exif.gps.date, ...
    - `datetime.timedelta` : exif.exif.offsettimeoriginal, exif.exif.offsettimedigitized, ...

    Attributes:
        lowercase_keys (bool): Whether to lowercase all EXIF keys (Default: true)

    :returns:
        ``{exif}`` -- a dict of all the collected exif inforamtion available in the
        file. Typically it consists of the following tags (if present in the file):

        - ``{exif.image}`` -- information related to the main image
        - ``{exif.exif}`` -- Exif information
        - ``{exif.gps}`` -- GPS information
        - ``{exif.interoperability}`` -- Interoperability information
    """

    filter_tags: Dict
    lowercase_keys: bool = True

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="exif",
        files=True,
        dirs=False,
    )

    def __init__(
        self,
        *args,
        filter_tags: Optional[Dict] = None,
        lowercase_keys: bool = True,
        **kwargs,
    ):
        # exif filter is used differently from other filters. The **kwargs are not
        # filter parameters but all belong into the filter_tags dictionary to filter
        # for specific exif tags.
        params = filter_tags or dict()
        params.update(kwargs)
        # *args are tags filtered without a value, like ["gps", "image.model"].
        for arg in args:
            params[arg] = None
        super().__init__(filter_tags=params, lowercase_keys=lowercase_keys)

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None, "Does not support standalone mode"

        # gather the exif data in a dict
        if exiftool_available():
            data = exiftool_read(path=res.path)
        else:
            data = exifread_read(path=res.path)

        # lowercase keys if wanted
        if self.lowercase_keys:
            data = lowercase_keys_recursive(data)

        # convert strings to datetime objects where possible
        parsed = convert_recursive(data)

        res.vars[self.filter_config.name] = parsed
        return matches_tags(self.filter_tags, data)


if __name__ == "__main__":
    import sys

    # Usage:
    # python organize/filters/exif.py tests/resources/images-with-exif/3.jpg
    data = exifread_read(Path(sys.argv[1]))
    print("Exifread", data)
    if exiftool_available():
        data = exiftool_read(Path(sys.argv[1]))
        print("Exiftool", data)
    else:
        print("Exiftool not available")
