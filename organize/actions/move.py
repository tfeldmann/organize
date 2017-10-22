import os
import shutil
import logging
from pathlib import Path
from .action import Action

logger = logging.getLogger(__name__)


class Move(Action):

    """
    Move a file to a new location. The file can also be renamed.
    If the specified path does not exist it will be created.

    If you only want to rename the file and keep the folder, it is
    easier to use the Rename-Action.

    :param str dest:
        can be a format string which uses file attributes from a filter.
        If `dest` is a folder path, the file will be moved into this folder and
        not renamed.

    :param bool overwrite:
        specifies whether existing files should be overwritten.
        Otherwise it will start enumerating files (append a counter to the
        filename) to resolve naming conflicts. [Default: False]

    Examples:
        - Move into `some/folder/` and keep filenames

          .. code-block:: yaml

              filters:
                - Move: {dest: '/some/folder/'}

        - Move to `some/path/` and change the name to include the full date

          .. code-block:: yaml

              - Move: {dest: '/some/path/some-name-{year}-{month:02}-{day:02}.pdf'}

        - Move into the folder `Invoices` on the same folder level as the file
          itself. Keep the filename but do not overwrite existing files (adds
          an index to the file)

          .. code-block:: yaml

              - Move: {dest: '{path.parent}/Invoices', overwrite: False}
    """

    def __init__(self, dest, overwrite=False):
        self.dest = dest
        self.overwrite = overwrite

    def run(self, path: Path, attrs: dict, simulate: bool):
        full_dest = self.dest.format(path=path, **attrs)

        # if only a folder path is given we append the filename to have the full
        # path. We use os.path for that because pathlib removes trailing slashes
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

    def _delete(self, path: Path, simulate: bool):
        self.print('Delete "%s"' % path)
        if not simulate:
            os.remove(path)

    def _move(self, src: Path, dest: Path, simulate):
        self.print('Move to "%s"' % dest)
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
