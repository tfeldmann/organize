import logging
from fs.base import FS
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

    @classmethod
    def get_schema(cls):
        return cls.name

    def pipeline(self, args: dict, simulate: bool):
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]  # type: str
        relative_path = args["relative_path"]
        self.print('Deleting "%s"' % relative_path)
        if not simulate:
            logger.info("Deleting %s.", relative_path)
            if fs.isdir(fs_path):
                fs.removetree(fs_path)
            elif fs.isfile(fs_path):
                fs.remove(fs_path)
