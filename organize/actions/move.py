import logging
import os
import shutil
from typing import Mapping

from pathlib import Path
from organize.utils import DotDict, find_unused_filename, fullpath

from .action import Action
from .trash import Trash

logger = logging.getLogger(__name__)


class Move(Action):

    """
    Move a file to a new location. The file can also be renamed.
    If the specified path does not exist it will be created.

    If you only want to rename the file and keep the folder, it is
    easier to use the Rename-Action.

    :param str dest:
        The destination folder or path.
        If `dest` ends with a slash / backslash, the file will be moved into
        this folder and not renamed.

    :param bool overwrite:
        specifies whether existing files should be overwritten.
        Otherwise it will start enumerating files (append a counter to the
        filename) to resolve naming conflicts. [Default: False]

    :param str counter_separator:
        specifies the separator between filename and the appended counter.
        Only relevant if **overwrite** is disabled. [Default: ``\' \'``]

    Examples:
        - Move all pdfs and jpgs from the desktop into the folder "~/Desktop/media/".
          Filenames are not changed.

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Desktop
                filters:
                  - extension:
                      - pdf
                      - jpg
                actions:
                  - move: '~/Desktop/media/'

        - Use a placeholder to move all .pdf files into a "PDF" folder and all
          .jpg files into a "JPG" folder. Existing files will be overwritten.

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Desktop
                filters:
                  - extension:
                      - pdf
                      - jpg
                actions:
                  - move:
                      dest: '~/Desktop/{extension.upper}/'
                      overwrite: true

        - Move pdfs into the folder `Invoices`. Keep the filename but do not
          overwrite existing files. To prevent overwriting files, an index is
          added to the filename, so ``somefile.jpg`` becomes ``somefile 2.jpg``.

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Desktop/Invoices
                filters:
                  - extension:
                      - pdf
                actions:
                  - move:
                      dest: '~/Documents/Invoices/'
                      overwrite: false
                      counter_separator: '_'
    """

    def __init__(self, dest: str, overwrite=False, counter_separator=" "):
        self.dest = dest
        self.overwrite = overwrite
        self.counter_separator = counter_separator

    def pipeline(self, args: DotDict, simulate: bool) -> Mapping[str, Path]:
        path = args["path"]

        expanded_dest = self.fill_template_tags(self.dest, args)
        # if only a folder path is given we append the filename to have the full
        # path. We use os.path for that because pathlib removes trailing slashes
        if expanded_dest.endswith(("\\", "/")):
            expanded_dest = os.path.join(expanded_dest, path.name)

        new_path = fullpath(expanded_dest)
        new_path_exists = new_path.exists()
        new_path_samefile = new_path_exists and new_path.samefile(path)
        if new_path_exists and not new_path_samefile:
            if self.overwrite:
                self.print("File already exists")
                Trash().run(path=new_path, simulate=simulate)
            else:
                new_path = find_unused_filename(
                    path=new_path, separator=self.counter_separator
                )

        if new_path_samefile and new_path == path:
            self.print("Keep location")
        else:
            self.print('Move to "%s"' % new_path)
            if not simulate:
                logger.info("Creating folder if not exists: %s", new_path.parent)
                new_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info('Moving "%s" to "%s"', path, new_path)
                shutil.move(src=str(path), dst=str(new_path))

        return {"path": new_path}

    def __str__(self) -> str:
        return "Move(dest=%s, overwrite=%s)" % (self.dest, self.overwrite)

    name = "move"
