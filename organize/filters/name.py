from typing import Any, List, Union, Optional, Dict

import simplematch  # type: ignore
from fs.path import basename
from pathlib import Path

from .filter import Filter


class Name(Filter):
    """
    Match files by filename

    :param str match:
        A matching string in `simplematch`-syntax
        (https://github.com/tfeldmann/simplematch)

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

    name = "name"
    schema_support_instance_without_args = True

    def __init__(
        self,
        match="{__fullname__}",
        *,
        startswith="",
        contains="",
        endswith="",
        case_sensitive=True,
    ) -> None:
        self.matcher = simplematch.Matcher(match, case_sensitive=case_sensitive)
        self.startswith = self.create_list(startswith, case_sensitive)
        self.contains = self.create_list(contains, case_sensitive)
        self.endswith = self.create_list(endswith, case_sensitive)
        self.case_sensitive = case_sensitive

    def matches(self, name: str) -> bool:
        if not self.case_sensitive:
            name = name.lower()

        is_match = (
            self.matcher.test(name)
            and any(x in name for x in self.contains)
            and any(name.startswith(x) for x in self.startswith)
            and any(name.endswith(x) for x in self.endswith)
        )
        return is_match

    def pipeline(self, args: Dict) -> Optional[Dict[str, Any]]:
        name = basename(args["fs_path"])
        result = self.matches(name)

        if result:
            m = self.matcher.match(name)
            if "__fullname__" in m:
                m = m["__fullname__"]
            return {self.get_name(): m}
        return None

    @staticmethod
    def create_list(x: Union[int, str, List[Any]], case_sensitive: bool) -> List[str]:
        if isinstance(x, (int, float)):
            x = str(x)
        if isinstance(x, str):
            x = [x]
        x = [str(x) for x in x]
        if not case_sensitive:
            x = [x.lower() for x in x]
        return x
