import re
from typing import Any, Dict, Mapping, Optional

import textract  # type: ignore
from organize.compat import Path

from .filter import Filter


# not supported: .gif, .jpg, .mp3, .ogg, .png, .tiff, .wav
SUPPORTED_EXTENSIONS = (
    ".csv .doc .docx .eml .epub .json .html .msg .odt .pdf .pptx .ps .rtf .txt .xlsx .xls"
).split()


class FileContent(Filter):

    r"""
    Matches file content with the given regular expression

    :param str expr:
        The regular expression to be matched.

    Any named groups in your regular expression will be returned like this:

    :returns:
        - ``{filecontent.yourgroupname}`` -- The text matched with the named group
          ``(?P<yourgroupname>)``

    Examples:

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

    def matches(self, path: Path) -> Any:
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return
        try:
            content = textract.process(str(path), errors="ignore")
            return self.expr.search(content.decode("utf-8", errors="ignore"))
        except textract.exceptions.CommandLineError:
            pass

    def pipeline(self, args: Mapping) -> Optional[Dict[str, Dict]]:
        match = self.matches(args["path"])
        if match:
            result = match.groupdict()
            return {"filecontent": result}
        return None
