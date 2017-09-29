import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Move:

    """ Move files

        Options:
            dest [str]
                `dest` can be a format string which uses file attributes from a
                filter.
                If `dest` is a folder path, the file will be moved into this
                folder and not renamed.

            overwrite=False [bool]
                `overwrite` specifies whether existing files should be
                overwritten. Otherwise it will start enumerating files (append a
                counter to the filename) to resolve naming conflicts.

        Examples:
            Move: {dest: '/some/folder/'}
            Move: {dest: '/some/path/some-name-{year}-{month:02}-{day:02}.pdf'}
            Move: {dest: '{path.parent}/Invoice', overwrite: False}
    """

    def __init__(self, dest: str, overwrite=False):
        self.dest = dest
        self.overwrite = overwrite

    def run(self, path: Path, file_attributes: dict, simulate: bool):
        full_dest = self.dest.format(path=path, **file_attributes)

        # if only a folder path is given we append the filename to be able to
        # check for existing files. full_dest is then a full file path.
        if full_dest.endswith(os.path.sep):
            full_dest = Path(os.path.join(full_dest, path.name))

        new_path = Path(full_dest).expanduser()
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
        return new_path

    @staticmethod
    def _delete(path: Path, simulate: bool):
        logger.info('Delete "%s"', path)
        if not simulate:
            os.remove(path)

    @staticmethod
    def _move(src: Path, dest: Path, simulate):
        logger.info('Move to "%s"', dest)
        if not simulate:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src=str(src), dst=str(dest))

    @staticmethod
    def _path_with_count(path: Path, count: int):
        return path.with_name('%s %s%s' % (path.stem, count, path.suffix))

    def __str__(self):
        return 'Move(dest=%s, overwrite=%s)' % (self.dest, self.overwrite)

    def __repr__(self):
        return '<' + str(self) + '>'
