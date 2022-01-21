import os
import logging
from typing import Mapping

from pathlib import Path

from .action import Action

logger = logging.getLogger(__name__)


class Delete(Action):

    """
    Delete a file from disk.

    Deleted files have no recovery option!
    Using the `Trash` action is strongly advised for most use-cases!

    Example:
        - Delete all JPGs and PNGs on the desktop which are older than one year:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
              - filters:
                  - lastmodified:
                      - days: 365
                  - extension:
                      - png
                      - jpg
              - actions:
                  - delete
    """

    name = "delete"

    def pipeline(self, args: Mapping, simulate: bool):
        path = args["path"]  # type: Path
        self.print('Delete "%s"' % path)
        if not simulate:
            logger.info("Deleting file %s.", path)
            os.remove(str(path))
