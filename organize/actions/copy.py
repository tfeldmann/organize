import logging
import os
import shutil

from organize.utils import Mapping, find_unused_filename, fullpath

from .action import Action
from .trash import Trash

logger = logging.getLogger(__name__)


CONFLICT_OPTIONS = ("rename_new", "rename_old", "skip", "trash", "overwrite")


class Copy(Action):
    name = "copy"

    """
    Copy a file to a new location.
    If the specified path does not exist it will be created.

    :param str dest:
        The destination where the file should be copied to.
        If `dest` ends with a slash / backslash, the file will be copied into
        this folder and keep its original name.

    :param bool overwrite:
        specifies whether existing files should be overwritten.
        Otherwise it will start enumerating files (append a counter to the
        filename) to resolve naming conflicts. [Default: False]

    :param str counter_separator:
        specifies the separator between filename and the appended counter.
        Only relevant if **overwrite** is disabled. [Default: ``\' \'``]

    Examples:
        - Copy all pdfs into `~/Desktop/somefolder/` and keep filenames

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Desktop
                filters:
                  - extension: pdf
                actions:
                  - copy: '~/Desktop/somefolder/'

        - Use a placeholder to copy all .pdf files into a "PDF" folder and all .jpg
          files into a "JPG" folder. Existing files will be overwritten.

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Desktop
                filters:
                  - extension:
                      - pdf
                      - jpg
                actions:
                  - copy:
                      dest: '~/Desktop/{extension.upper}/'
                      overwrite: true

        - Copy into the folder `Invoices`. Keep the filename but do not
          overwrite existing files. To prevent overwriting files, an index is
          added to the filename, so `somefile.jpg` becomes `somefile 2.jpg`.
          The counter separator is `' '` by default, but can be changed using
          the `counter_separator` property.

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: ~/Desktop/Invoices
                filters:
                  - extension:
                      - pdf
                actions:
                  - copy:
                      dest: '~/Documents/Invoices/'
                      overwrite: false
                      counter_separator: '_'
    """

    def __init__(
        self, dest: str, on_conflict="rename_new", counter_separator=" "
    ) -> None:
        if on_conflict not in CONFLICT_OPTIONS:
            raise ValueError(
                "on_conflict must be one of %s" % ", ".join(CONFLICT_OPTIONS)
            )
        self.dest = dest
        self.on_conflict = on_conflict
        self.counter_separator = counter_separator

    def pipeline(self, args: Mapping, simulate: bool) -> None:
        path = args["path"]

        expanded_dest = self.fill_template_tags(self.dest, args)
        # if only a folder path is given we append the filename to have the full
        # path. We use os.path for that because pathlib removes trailing slashes
        if expanded_dest.endswith(("\\", "/")):
            expanded_dest = os.path.join(expanded_dest, path.name)

        new_path = fullpath(expanded_dest)
        if new_path.exists() and not new_path.samefile(path):
            if self.overwrite:
                self.print("File already exists")
                Trash().run(path=new_path, simulate=simulate)
            else:
                new_path = find_unused_filename(
                    path=new_path, separator=self.counter_separator
                )

        self.print('Copy to "%s"' % new_path)
        if not simulate:
            logger.info("Creating folder if not exists: %s", new_path.parent)
            new_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info('Copying "%s" to "%s"', path, new_path)
            shutil.copy2(src=str(path), dst=str(new_path))

        # the next actions should handle the original file
        return None

    def __str__(self) -> str:
        return "Copy(dest=%s, on_conflict=%s)" % (self.dest, self.on_conflict)
