import logging
import re
from typing import Any

from fs.base import FS
from fs.errors import NoSysPath
from pydantic import Field
from typing_extensions import Literal

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

    name: Literal["filecontent"] = Field("filecontent", repr=False)
    expr: str = r"(?P<all>.*)"

    _expr: re.Pattern

    class ParseConfig:
        accepts_positional_arg = "expr"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._expr = re.compile(self.expr, re.MULTILINE | re.DOTALL)

    def matches(self, path: str) -> Any:
        try:
            import textract

            content = textract.process(
                str(path),
                errors="ignore",
            )
            match = self._expr.search(content.decode("utf-8", errors="ignore"))
            return match
        except ImportError as e:
            raise ImportError(
                "textract is not installed. "
                "Install with pip install organize-tool[textract]"
            ) from e
        except textract.exceptions.CommandLineError as e:
            logger.exception(e)

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
