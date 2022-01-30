import re
from typing import Any, Dict, Mapping, Optional

from .filter import Filter, FilterResult


class Regex(Filter):

    r"""Matches filenames with the given regular expression

    Args:
        expr (str): The regular expression to be matched.

    **Returns:**

    Any named groups in your regular expression will be returned like this:

    - `{regex.groupname}`: The text matched with the named
      group `(?P<groupname>.*)`

    """

    name = "regex"

    def __init__(self, expr) -> None:
        self.expr = re.compile(expr, flags=re.UNICODE)

    def matches(self, path: str) -> Any:
        return self.expr.search(path)

    def pipeline(self, args: dict) -> FilterResult:
        match = self.matches(args["relative_path"])
        return FilterResult(
            matches=bool(match),
            updates={
                self.get_name(): match.groupdict(),
            },
        )
