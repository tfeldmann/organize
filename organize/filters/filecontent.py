import re
from typing import Any, Dict, Mapping, Optional

from fs.base import FS
from fs.errors import NoSysPath

from .filter import Filter, FilterResult

SUPPORTED_EXTENSIONS = (
    # not supported: .gif, .jpg, .mp3, .ogg, .png, .tiff, .wav
    ".csv .doc .docx .eml .epub .json .html .msg .odt .pdf .pptx .ps .rtf .txt .xlsx .xls"
).split()


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

    def __init__(self, expr) -> None:
        self.expr = re.compile(expr, re.MULTILINE | re.DOTALL)

    def matches(self, path: str, extension: str) -> Any:
        if extension not in SUPPORTED_EXTENSIONS:
            return
        try:
            import textract

            content = textract.process(
                str(path),
                extension=extension,
                errors="ignore",
            )
            return self.expr.search(content.decode("utf-8", errors="ignore"))
        except ImportError as e:
            raise ImportError(
                "textract is not installed. "
                "Install with pip install organize-tool[textract]"
            ) from e
        except textract.exceptions.CommandLineError:
            pass

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]
        if fs.isdir(fs_path):
            raise ValueError("Dirs not supported")
        extension = fs.getinfo(fs_path).suffix
        try:
            syspath = fs.getsyspath(fs_path)
        except NoSysPath as e:
            raise EnvironmentError(
                "filecontent only supports the local filesystem"
            ) from e
        match = self.matches(path=syspath, extension=extension)
        return FilterResult(
            matches=match,
            updates={self.get_name(): match.groupdict()},
        )
