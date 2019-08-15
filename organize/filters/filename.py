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

        - Match all files starting with 'A' or 'B' containing '5' or '6' and ending with
          '_end'

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - filename:
                      startswith:
                        - A
                        - B
                      contains:
                        - 5
                        - 6
                      endswith: _end
                      case_sensitive: false
                actions:
                  - echo: 'Found a match.'
    """

    def __init__(self, startswith="", contains="", endswith="", case_sensitive=True):
        self.startswith = self.create_list(startswith, case_sensitive)
        self.contains = self.create_list(contains, case_sensitive)
        self.endswith = self.create_list(endswith, case_sensitive)
        self.case_sensitive = case_sensitive

    def matches(self, path):
        filename = path.stem
        if not self.case_sensitive:
            filename = filename.lower()
        return (
            any(x in filename for x in self.contains)
            and any(filename.startswith(x) for x in self.startswith)
            and any(filename.endswith(x) for x in self.endswith)
        )

    def pipeline(self, args):
        return self.matches(args.path)

    @staticmethod
    def create_list(x, case_sensitive):
        if isinstance(x, str):
            x = [x]
        x = [str(x) for x in x]
        if not case_sensitive:
            x = [x.lower() for x in x]
        return x
