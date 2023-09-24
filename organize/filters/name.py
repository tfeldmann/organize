from typing import Any, ClassVar, Dict, List, Union

import simplematch
from fs import path
from pydantic import Field
from typing_extensions import Literal

from organize.output import Output
from organize.resource import Resource

from . import FilterConfig
from .filter import Filter, FilterResult


class Name:
    """Match files and folders by name

    Args:
        match (str):
            A matching string in [simplematch-syntax](https://github.com/tfeldmann/simplematch)

        startswith (str):
            The filename must begin with the given string

        contains (str):
            The filename must contain the given string

        endswith (str):
            The filename (without extension) must end with the given string

        case_sensitive (bool):
            By default, the matching is case sensitive. Change this to False to use
            case insensitive matching.
    """

    match: str = "*"
    startswith: Union[str, List[str]] = ""
    contains: Union[str, List[str]] = ""
    endswith: Union[str, List[str]] = ""
    case_sensitive: bool = True

    filter_config: ClassVar = FilterConfig(name="name", files=True, dirs=True)

    def __post_init__(self, *args, **kwargs):
        self._matcher = simplematch.Matcher(
            self.match,
            case_sensitive=self.case_sensitive,
        )
        self.startswith = self.create_list(self.startswith, self.case_sensitive)
        self.contains = self.create_list(self.contains, self.case_sensitive)
        self.endswith = self.create_list(self.endswith, self.case_sensitive)

    def matches(self, name: str) -> bool:
        if not self.case_sensitive:
            name = name.lower()

        is_match = (
            self._matcher.test(name)
            and any(x in name for x in self.contains)
            and any(name.startswith(x) for x in self.startswith)
            and any(name.endswith(x) for x in self.endswith)
        )
        return is_match

    def pipeline(self, res: Resource, output: Output) -> bool:
        fs = args["fs"]
        fs_path = args["fs_path"]
        if fs.isdir(fs_path):
            name = path.basename(fs_path)
        else:
            name, ext = path.splitext(path.basename(fs_path))
            if not name:
                name = ext
        result = self.matches(name)
        m = self._matcher.match(name)
        if m == {}:
            m = name
        return FilterResult(
            matches=result,
            updates={self.name: m},
        )

    @staticmethod
    def create_list(x: Union[int, str, List[Any]], case_sensitive: bool) -> List[str]:
        if isinstance(x, (int, float)):
            x = str(x)
        if isinstance(x, str):
            x = [x]
        x = [str(x) for x in x]
        if not case_sensitive:
            x = [x.lower() for x in x]
        return x
