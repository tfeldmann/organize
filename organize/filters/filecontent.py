import re
from typing import Any, Dict, Mapping, Optional

from fs.errors import NoSysPath

from .filter import Filter

SUPPORTED_EXTENSIONS = (
    # not supported: .gif, .jpg, .mp3, .ogg, .png, .tiff, .wav
    ".csv .doc .docx .eml .epub .json .html .msg .odt .pdf .pptx .ps .rtf .txt .xlsx .xls"
).split()


class FileContent(Filter):
    name = "filecontent"

    r"""
    Matches file content with the given regular expression

    :param str expr:
        The regular expression to be matched.

    Any named groups in your regular expression will be returned like this:

    :returns:
        - ``{filecontent.yourgroupname}`` -- The text matched with the named group
          ``(?P<yourgroupname>)``

    Examples:

        - Show the content of all your PDF files:

          .. code-block::yaml
            :caption: config.yaml

            rules:
              - folders: ~/Documents
                filters:
                  - extension: pdf
                  - filecontent: '(?P<all>.*)'
                actions:
                  - echo: "{filecontent.all}"


        - Match an invoice with a regular expression and sort by customer:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - filecontent: 'Invoice.*Customer (?P<customer>\w+)'
                actions:
                  - move: '~/Documents/Invoices/{filecontent.customer}/'
    """

    def __init__(self, expr) -> None:
        self.expr = re.compile(expr, re.MULTILINE | re.DOTALL)

    def matches(self, path: str, extension: str) -> Any:
        if extension not in SUPPORTED_EXTENSIONS:
            return
        try:
            import textract  # type: ignore

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

    def pipeline(self, args: Mapping) -> Optional[Dict[str, Dict]]:
        fs = args["fs"]
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
        if match:
            result = match.groupdict()
            return {"filecontent": result}
        return None
