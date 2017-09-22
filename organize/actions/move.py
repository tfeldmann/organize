import logging
from pathlib import Path
logger = logging.getLogger(__name__)


class Move:

    """ Move files

        Usage:
            Move(dest, overwrite=False)

            `dest` can be a format string which uses file attributes from a
            filter.
            If `dest` is a folder path, the file will be moved into this folder
            and not renamed.

            `overwrite` specifies whether existing files should be overwritten.
            Otherwise it will append a counter to the filename to resolve
            conflicts.

        Example:
            Move('/some/path/')
            Move('/some/path/some-name-{year}-{month:02}-{day:02}.pdf')

    """

    def __init__(self, dest: str, overwrite=False):
        self.dest = dest
        self.overwrite = overwrite

    def run(self, path: Path, file_attributes: dict, simulate: bool):
        new_path = (
            Path(self.dest.format(path=path, **file_attributes)).expanduser())

        # if only a folder path is given we append the filename to be able to
        # check for existing files. new_path is then a full file path.
        if new_path.is_dir():
            new_path = new_path / path.name

        if new_path.exists():
            if self.overwrite:
                self._delete(path=new_path, simulate=simulate)
            else:
                # rename
                count = 2
                while new_path.exists():
                    new_path = self._path_with_count(new_path, count)
                    count += 1

        self._move(src=path, dest=new_path, simulate=simulate)

    @staticmethod
    def _delete(path: Path, simulate: bool):
        logger.info('Delete "%s"', path)
        if not simulate:
            import os
            os.remove(path)

    @staticmethod
    def _move(src: Path, dest: Path, simulate):
        logger.info('Move to "%s"', dest)
        if not simulate:
            import shutil
            shutil.move(src=src.expanduser(), dst=dest.expanduser())

    @staticmethod
    def _path_with_count(path: Path, count: int):
        return path.with_name('%s %s%s' % (path.stem, count, path.suffix))

    def __str__(self):
        return 'Move(dest=%s, overwrite=%s)' % (self.dest, self.overwrite)

    def __repr__(self):
        return '<' + str(self) + '>'
