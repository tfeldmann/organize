import re
from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Regex:

    """Matches filenames with the given regular expression

    Args:
        expr (str): The regular expression to be matched.

    **Returns:**

    Any named groups in your regular expression will be returned like this:

    - `{regex.groupname}`: The text matched with the named
      group `(?P<groupname>.*)`

    """

    expr: str

    filter_config: ClassVar = FilterConfig(name="regex", files=True, dirs=True)

    def __post_init__(self):
        self._expr = re.compile(self.expr, flags=re.UNICODE)

    def matches(self, path: str):
        return self._expr.search(path)

    def pipeline(self, res: Resource, output: Output) -> bool:
        match = self.matches(res.path.name)
        if match:
            res.deep_merge(key=self.filter_config.name, data=match.groupdict())
            return True
        return False
