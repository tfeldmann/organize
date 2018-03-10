import logging

from organize.utils import Path
from .action import Action


class Trash(Action):

    """
    Move a file into the trash.

    Example:
        - Move all JPGs and PNGs on the desktop which are older than one year
          into the trash:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
              - filters:
                  - LastModified:
                      - days: 365
                  - Extension:
                      - png
                      - jpg
              - actions:
                  - Trash
    """

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def run(self, basedir: Path, path: Path, attrs: dict, simulate: bool):
        from send2trash import send2trash
        self.print('Trash "%s"' % path)
        if not simulate:
            expanded_path = path.expanduser()
            self.log.info('Moving file %s into trash.', expanded_path)
            send2trash(str(expanded_path))
