import logging
from pathlib import Path
logger = logging.getLogger(__name__)


class Move:

    """ Move files

        Usage:
            Move(dest)
            `dest` can be a format string which uses file attributes from a
            filter.

            If `dest` is a folder path, the file will be moved into this folder
            and not renamed.

        Example:
            Move('/some/path/')
            Move('/some/path/some-name-{year}-{month:02}-{day:02}.pdf')

    """

    def __init__(self, dest):
        self.dest = dest

    def run(self, path, file_attributes, simulate):
        new_path = Path(self.dest.format(path=path, **file_attributes))
        if simulate:
            logger.info('Moving %s to %s', path, new_path)
        else:
            import shutil
            shutil.move(src=path.expanduser(), dst=new_path.expanduser())
