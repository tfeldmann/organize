import logging

from organize.utils import Path
from .action import Action

logger = logging.getLogger(__name__)


class Trash(Action):

    """
    Move a file into the trash.

    Example:
        - Move all JPGs and PNGs on the desktop which are older than one year
          into the trash:

          .. code-block:: yaml

              rules:
              - folders: '~/Desktop'
              - filters:
                  - OlderThan: {years: 1}
                  - Extension:
                      - png
                      - jpg
              - actions:
                  - Trash
    """

    def run(self, path, attrs, simulate):  # type: (Path, dict, bool) -> None
        from send2trash import send2trash
        self.print('Trash "%s"' % path)
        if not simulate:
            send2trash(str(path.expanduser()))
