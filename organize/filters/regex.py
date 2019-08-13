import re
from organize.utils import DotDict
from .filter import Filter


class Regex(Filter):

    """
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
    """

    def __init__(self, expr):
        self.expr = re.compile(expr, flags=re.UNICODE)

    def run(self, path):
        match = self.expr.match(path.name)
        if match:
            result = DotDict(match.groupdict())
            return {"regex": result}
