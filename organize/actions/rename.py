import os
import shutil
import logging

from organize.utils import Path
from .move import Move

logger = logging.getLogger(__name__)


class Rename(Move):

    """
    Renames a file.
    If the specified path does not exist it will be created.

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
                - Move: {dest: '~/some/folder/'}

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
        self.dest = os.path.join('{path.parent}', dest)
        self.overwrite = overwrite

    def move(self, src: Path, dest: Path, simulate):
        self.print('Rename to "%s"' % dest)
        if not simulate:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src=str(src), dst=str(dest))

    def __str__(self):
        return 'Rename(dest=%s, overwrite=%s)' % (self.dest, self.overwrite)
