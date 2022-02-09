import logging

from fs.base import FS

from organize.utils import safe_description

from .action import Action

logger = logging.getLogger(__name__)


class Delete(Action):

    """
    Delete a file from disk.

    Deleted files have no recovery option!
    Using the `Trash` action is strongly advised for most use-cases!
    """

    name = "delete"

    @classmethod
    def get_schema(cls):
        return cls.name

    def pipeline(self, args: dict, simulate: bool):
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]  # type: str
        desc = safe_description(fs=fs, path=fs_path)
        self.print('Deleting "%s"' % desc)
        if not simulate:
            logger.info("Deleting %s.", desc)
            if fs.isdir(fs_path):
                fs.removetree(fs_path)
            elif fs.isfile(fs_path):
                fs.remove(fs_path)
