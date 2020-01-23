import re
from typing import Any, Dict, Mapping, Optional

import textract  # type: ignore
from organize.compat import Path

from .filter import Filter


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
        self.expr = re.compile(expr)

    def matches(self, path: Path) -> Any:
        content = textract.process(str(path))
        return self.expr.search(content.decode("utf-8"))

    def pipeline(self, args: Mapping) -> Optional[Dict[str, Dict]]:
        match = self.matches(args["path"])
        if match:
            result = match.groupdict()
            return {"filecontent": result}
        return None
