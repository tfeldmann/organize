from typing import Any, ClassVar, List, Union

import simplematch
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
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

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="name", files=True, dirs=True
    )

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
        assert res.path is not None, "Does not support standalone mode"
        if res.is_dir():
            name = res.path.stem
        else:
            name, ext = res.path.stem, res.path.suffix
            if not name:
                name = ext
        result = self.matches(name)
        m = self._matcher.match(name)
        if m == {}:
            m = name

        res.vars[self.filter_config.name] = m
        return result

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
