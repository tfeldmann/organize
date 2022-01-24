import logging

from fs import open_fs
from fs.base import FS
from fs.copy import copy_file
from fs.move import move_file
from fs.path import basename, dirname, join, splitext
from schema import Optional, Or

from ..utils import JinjaEnv, file_desc, next_free_filename
from .action import Action
from .trash import Trash

logger = logging.getLogger(__name__)


CONFLICT_OPTIONS = (
    "skip",
    "overwrite",
    "trash",
    "rename_new",
    "rename_existing",
    # "keep_newer",
    # "keep_older",
)


class Copy(Action):

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

    name = "copy"
    arg_schema = Or(
        str,
        {
            "dest": str,
            Optional("conflict_mode"): Or(*CONFLICT_OPTIONS),
            Optional("rename_template"): str,
        },
    )

    def __init__(
        self,
        dest: str,
        conflict_mode="rename_new",
        rename_template="{name} {counter}{extension}",
    ) -> None:
        if conflict_mode not in CONFLICT_OPTIONS:
            raise ValueError(
                "conflict_mode must be one of %s" % ", ".join(CONFLICT_OPTIONS)
            )

        self.dest = JinjaEnv.from_string(dest)
        self.conflict_mode = conflict_mode
        self.rename_template = JinjaEnv.from_string(rename_template)

    def pipeline(self, args: dict, simulate: bool):
        src_fs = args["fs"]  # type: FS
        src_path = args["fs_path"]

        dst_path = self.dst.render(**args)
        # if the destination ends with a slash we assume the name should not change
        if dst_path.endswith(("\\", "/")):
            dst_path = join(dst_path, basename(src_path))

        dst_fs = open_fs(dirname(dst_path), writeable=True, create=True)
        dst_path = basename(dst_path)

        if dst_fs.exists(dst_path):
            self.print(
                'File %s already exists (conflict mode is "%s").'
                % (file_desc(dst_fs, dst_path), self.conflict_mode)
            )

            if self.conflict_mode == "trash":
                Trash().pipeline({"fs": dst_fs, "fs_path": dst_path}, simulate=simulate)
                if not simulate:
                    copy_file(src_fs, src_path, dst_fs, dst_path)
                self.print("Copied to %s." % file_desc(dst_fs, dst_path))

            elif self.conflict_mode == "skip":
                self.print("Skipped.")
                return

            elif self.conflict_mode == "overwrite":
                if not simulate:
                    copy_file(src_fs, src_path, dst_fs, dst_path)
                self.print("Copied to %s (overwritten)." % file_desc(dst_fs, dst_path))

            elif self.conflict_mode == "rename_new":
                stem, ext = splitext(dst_path)
                name = next_free_filename(
                    fs=dst_fs,
                    name=stem,
                    extension=ext,
                    template=self.rename_template,
                )
                if not simulate:
                    copy_file(src_fs, src_path, dst_fs, name)
                self.print("Copied to %s" % file_desc(dst_fs, name))

            elif self.conflict_mode == "rename_existing":
                stem, ext = splitext(dst_path)
                name = next_free_filename(
                    fs=dst_fs,
                    name=stem,
                    extension=ext,
                    template=self.rename_template,
                )
                self.print("Renaming existing file to: %s" % name)
                if not simulate:
                    move_file(dst_fs, dst_path, dst_fs, name)
                    copy_file(src_fs, src_path, dst_fs, dst_path)
                self.print("Copied to %s" % file_desc(dst_fs, dst_path))
        else:
            if not simulate:
                copy_file(src_fs, src_path, dst_fs, dst_path)
            self.print("Copied to %s" % file_desc(dst_fs, dst_path))

        # the next action should work with the newly created copy
        return {
            "fs": dst_fs,
            "fs_path": dst_path,
        }

    def __str__(self) -> str:
        return "Copy(dest=%s, conflict_mode=%s)" % (self.dest, self.conflict_mode)
