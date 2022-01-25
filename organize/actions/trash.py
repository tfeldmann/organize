import logging

from .action import Action

logger = logging.getLogger(__name__)


class Trash(Action):

    """Move a file or dir into the trash."""

    name = "trash"

    @classmethod
    def get_schema(cls):
        return cls.name

    def trash(self, path: str, simulate: bool):
        from send2trash import send2trash  # type: ignore

        self.print('Trash "%s"' % path)
        if not simulate:
            logger.info("Moving file %s into trash.", path)
            send2trash(path)

    def pipeline(self, args: dict, simulate: bool):
        fs = args["fs"]
        fs_path = args["fs_path"]
        self.trash(path=fs.getsyspath(fs_path), simulate=simulate)
