import collections
from typing import Any, DefaultDict, Dict, Mapping, Optional, Union

import exifread  # type: ignore

from organize.compat import Path

from .filter import Filter

ExifDict = Mapping[str, Union[str, Mapping[str, str]]]


class Exif(Filter):

    """
    Filter by EXIF data
    """

    def __init__(self, *args: str, **kwargs: str) -> None:
        self.args = args  # expected exif keys
        self.kwargs = kwargs  # exif keys with expected values

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
        # available in Python 3.8.
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
