import logging

from .action import Action

logger = logging.getLogger(__name__)


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

    name = "trash"

    def pipeline(self, args: dict, simulate: bool):
        from send2trash import send2trash  # type: ignore

        fs = args["fs"]
        fs_path = args["fs_path"]
        path = fs.getsyspath(fs_path)
        self.print('Trash "%s"' % path)
        if not simulate:
            logger.info("Moving file %s into trash.", path)
            send2trash(path)
