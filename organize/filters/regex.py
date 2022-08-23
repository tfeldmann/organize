import re

from fs.path import basename
from typing_extensions import Literal

from .filter import Filter, FilterResult


class Regex(Filter):

    """Matches filenames with the given regular expression

    Args:
        expr (str): The regular expression to be matched.

    **Returns:**

    Any named groups in your regular expression will be returned like this:

    - `{regex.groupname}`: The text matched with the named
      group `(?P<groupname>.*)`

    """

    name: Literal["regex"] = "regex"
    expr: str

    _expr: re.Pattern

    class ParseConfig:
        accepts_positional_arg = "expr"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._expr = re.compile(self.expr, flags=re.UNICODE)

    def matches(self, path: str):
        return self._expr.search(path)

    def pipeline(self, args: dict) -> FilterResult:
        fs_path = args["fs_path"]
        match = self.matches(basename(fs_path))
        return FilterResult(
            matches=bool(match),
            updates={
                self.name: match.groupdict() if match else "",
            },
        )
