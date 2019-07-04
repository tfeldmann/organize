from .filter import Filter


class Filename(Filter):

    """
    Match files by filename

    :param str startswith:
        The filename must begin with the given string

    :param str contains:
        The filename must contain the given string

    :param str endswith:
        The filename (without extension) must end with the given string

    :param bool case_sensitive = True:
        By default, the matching is case sensitive. Change this to False to use
        case insensitive matching.

    Examples:
        - Match all files starting with 'Invoice':

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - filename:
                      startswith: Invoice
                actions:
                  - echo: 'This is an invoice'

        - Match all files starting with 'A' end containing the string 'hole'
          (case insensitive)

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - filename:
                      startswith: A
                      contains: hole
                      case_sensitive: false
                actions:
                  - echo: 'Found a match.'
    """

    def __init__(self, startswith="", contains="", endswith="", case_sensitive=True):
        self.startswith = startswith
        self.contains = contains
        self.endswith = endswith
        self.case_sensitive = case_sensitive

        if not self.case_sensitive:
            self.startswith = self.startswith.lower()
            self.contains = self.contains.lower()
            self.endswith = self.endswith.lower()

    def matches(self, path):
        filename = self._filename(path)
        return (
            filename.startswith(self.startswith)
            and filename.endswith(self.endswith)
            and self.contains in filename
        )

    def _filename(self, path):
        if not self.case_sensitive:
            return path.stem.lower()
        else:
            return path.stem
