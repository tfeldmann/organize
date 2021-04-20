import sys
import logging
from typing import Mapping

from organize.compat import Path

from .action import Action

logger = logging.getLogger(__name__)


class MacOSTags(Action):

    """
    Add macOS tags.

    Example:
        - Adding a "Invoice" and "Important" tag:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Documents/Invoices'
              - filters:
                  - filename:
                      startswith: "Invoice"
                  - extension: pdf
              - actions:
                  - macos_tags:
                    - Important
                    - Invoice
    """

    def __init__(self, *tags):
        self.tags = tags

    def pipeline(self, args: Mapping):
        path = args["path"]  # type: Path
        simulate = args["simulate"]  # type: bool

        if sys.platform == "darwin":
            import macos_tags

            self.print("Adding tags: %s" % ", ".join(self.tags))
            print(self.tags)
            if not simulate:
                for tag in self.tags:
                    macos_tags.add(tag, file=str(path))
        else:
            self.print("The macos_tags action is only available on macOS")

    def __str__(self) -> str:
        return "MacOSTags(tags=%s)" % self.tags
