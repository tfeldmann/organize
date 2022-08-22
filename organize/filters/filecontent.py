import logging
import re
from typing import Any

from fs.base import FS
from fs.errors import NoSysPath

from .filter import Filter, FilterResult

logger = logging.getLogger(__name__)


class FileContent(Filter):
    """Matches file content with the given regular expression

    Args:
        expr (str): The regular expression to be matched.

    Any named groups (`(?P<groupname>.*)`) in your regular expression will
    be returned like this:

    **Returns:**

    - `{filecontent.groupname}`: The text matched with the named group
      `(?P<groupname>)`
    """

    name = "filecontent"
    schema_support_instance_without_args = True

    def __init__(self, expr="(?P<all>.*)") -> None:
        self.expr = re.compile(expr, re.MULTILINE | re.DOTALL)

    def matches(self, path: str) -> Any:
        try:
            import textract

            content = textract.process(
                str(path),
                errors="ignore",
            )
            match = self.expr.search(content.decode("utf-8", errors="ignore"))
            return match
        except ImportError as e:
            raise ImportError(
                "textract is not installed. "
                "Install with pip install organize-tool[textract]"
            ) from e
        except textract.exceptions.CommandLineError as e:
            pass

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]
        if fs.isdir(fs_path):
            raise ValueError("Dirs not supported")
        try:
            syspath = fs.getsyspath(fs_path)
        except NoSysPath as e:
            raise EnvironmentError(
                "filecontent only supports the local filesystem"
            ) from e
        match = self.matches(path=syspath)
        if match:
            updates = {self.name: match.groupdict()}
        else:
            updates = {}
        return FilterResult(
            matches=bool(match),
            updates=updates,
        )
