import os
import shutil
import logging
from .action import Action
from .trash import Trash

from organize.utils import Path, find_unused_filename

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

    def __init__(self, dest: str, overwrite=False):
        self.dest = dest
        self.overwrite = overwrite

    def run(self, path: Path, attrs: dict, simulate: bool):
        full_path = path.expanduser()

        expanded_dest = self.fill_template_tags(self.dest, path, attrs)
        # if only a folder path is given we append the filename to have the full
        # path. We use os.path for that because pathlib removes trailing slashes
        if expanded_dest.endswith(os.path.sep):
            expanded_dest = os.path.join(expanded_dest, path.name)

        new_path = Path(expanded_dest).expanduser()
        if new_path.exists() and not new_path.samefile(full_path):
            if self.overwrite:
                self.print('Overwriting existing file!')
                Trash().run(path=new_path, attrs=attrs, simulate=simulate)
            else:
                new_path = find_unused_filename(new_path)

        self.print('Move to "%s"' % new_path)
        if not simulate:
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src=str(full_path), dst=str(new_path))
        return new_path

    def __str__(self):
        return 'Move(dest=%s, overwrite=%s)' % (self.dest, self.overwrite)
