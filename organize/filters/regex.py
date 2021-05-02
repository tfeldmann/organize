import re
from typing import Any, Dict, Mapping, Optional

from pathlib import Path

from .filter import Filter


class Regex(Filter):

    r"""
    Matches filenames with the given regular expression

    :param str expr:
        The regular expression to be matched.

    Any named groups in your regular expression will be returned like this:

    :returns:
        - ``{regex.yourgroupname}`` -- The text matched with the named group
          ``(?P<yourgroupname>)``

    Examples:
        - Match an invoice with a regular expression:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - regex: '^RG(\d{12})-sig\.pdf$'
                actions:
                  - move: '~/Documents/Invoices/1und1/'

        - Match and extract data from filenames with regex named groups:
          This is just like the previous example but we rename the invoice using
          the invoice number extracted via the regular expression and the named
          group ``the_number``.

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Desktop
                filters:
                  - regex: '^RG(?P<the_number>\d{12})-sig\.pdf$'
                actions:
                  - move: ~/Documents/Invoices/1und1/{regex.the_number}.pdf
                - Match and extract data from filenames with regex named groups:
                
        - Another example to support debugging of filters is to echo the filecontent.
          This can be usefull if the file contains poorly formated text.
          group ``the_number``.

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Desktop
                filters:
                  - filecontent: '(?P<inhalt>.*)' 
                actions:
                  - echo: "Filecontent: {filecontent.inhalt}"
          
        - Exampe to filter the filename with respect to a valid date code.
          Example: Filename should start with <year>-<month>-<day>.
          Regex 
          1. creates a placeholder variable containing the year
          2. allows only years which start with 20 and are followed by 2 numbers
          3. months can only have as first digit 0 or 1 and must be followed by a number
          4. days can only have 0, 1 or 3 and must followed by number
          Note: Filter is not perfect but still.

          group ``the_number``.

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Desktop
                filters:
                  - regex: '(?P<year>20\d{2})-[01]\d-[013]\d.*'
                actions:
                  - echo: "Year: {regex.year}"
    """

    def __init__(self, expr) -> None:
        self.expr = re.compile(expr, flags=re.UNICODE)

    def matches(self, path: Path) -> Any:
        return self.expr.search(path.name)

    def pipeline(self, args: Mapping) -> Optional[Dict[str, Dict]]:
        match = self.matches(args["path"])
        if match:
            result = match.groupdict()
            return {"regex": result}
        return None
