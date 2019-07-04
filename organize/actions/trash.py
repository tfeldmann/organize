import logging

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
                  - lastmodified:
                      - days: 365
                  - extension:
                      - png
                      - jpg
              - actions:
                  - trash
    """

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def run(self, attrs: dict, simulate: bool):
        path = attrs["path"]
        from send2trash import send2trash

        self.print('Trash "%s"' % path)
        if not simulate:
            self.log.info("Moving file %s into trash.", path)
            send2trash(str(path))
