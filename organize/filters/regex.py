import re

from fs.path import basename

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

    name = "regex"

    arg_schema = str

    def __init__(self, expr) -> None:
        self.expr = re.compile(expr, flags=re.UNICODE)

    def matches(self, path: str):
        return self.expr.search(path)

    def pipeline(self, args: dict) -> FilterResult:
        match = self.matches(basename(args["fs_path"]))
        return FilterResult(
            matches=bool(match),
            updates={
                self.get_name(): match.groupdict() if match else "",
            },
        )
