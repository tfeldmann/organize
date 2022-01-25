import logging
import os

from fs import path
from fs.base import FS
from fs.move import move_dir, move_file
from schema import Optional, Or

from organize.utils import JinjaEnv, file_desc

from .action import Action
from .utils import CONFLICT_OPTIONS, resolve_overwrite_conflict

logger = logging.getLogger(__name__)


class Rename(Action):

    """
    Renames a file.

    :param str name:
        The new filename.
        Can be a format string which uses file attributes from a filter.

    :param bool overwrite:
        specifies whether existing files should be overwritten.
        Otherwise it will start enumerating files (append a counter to the
        filename) to resolve naming conflicts. [Default: False]

    :param str counter_separator:
        specifies the separator between filename and the appended counter.
        Only relevant if **overwrite** is disabled. [Default: ``\' \'``]

    Examples:
        - Convert all .PDF file extensions to lowercase (.pdf):

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - extension: PDF
                actions:
                  - rename: "{path.stem}.pdf"

        - Convert **all** file extensions to lowercase:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - Extension
                actions:
                  - rename: "{path.stem}.{extension.lower}"
    """

    name = "rename"
    arg_schema = Or(
        str,
        {
            "name": str,
            Optional("on_conflict"): Or(*CONFLICT_OPTIONS),
            Optional("rename_template"): str,
        },
    )

    def __init__(
        self,
        new_name: str,
        on_conflict="rename_new",
        rename_template="{name} {counter}{extension}",
    ) -> None:
        if on_conflict not in CONFLICT_OPTIONS:
            raise ValueError(
                "on_conflict must be one of %s" % ", ".join(CONFLICT_OPTIONS)
            )

        self.new_name = JinjaEnv.from_string(new_name)
        self.conflict_mode = on_conflict
        self.rename_template = JinjaEnv.from_string(rename_template)

    def pipeline(self, args: dict, simulate: bool):
        fs = args["fs"]  # type: FS
        src_path = args["fs_path"]

        new_name = self.new_name.render(**args)
        if os.path.sep in new_name:
            ValueError(
                "Rename only takes a name as argument. "
                "To move files or folders use the move action."
            )

        parents, full_name = path.split(src_path)
        name, ext = path.splitext(full_name)
        dst_path = path.join(parents, new_name)

        if dst_path == src_path:
            self.print("Name did not change")
        else:
            if fs.isdir(src_path):
                move_action = move_dir
            elif fs.isfile(src_path):
                move_action = move_file

            skip = False
            if fs.exists(dst_path):
                self.print(
                    '%s already exists (conflict mode is "%s").'
                    % (file_desc(fs, dst_path), self.conflict_mode)
                )
                fs, dst_path, skip = resolve_overwrite_conflict(
                    dst_fs=fs,
                    dst_path=dst_path,
                    conflict_mode=self.conflict_mode,
                    rename_template=self.rename_template,
                    simulate=simulate,
                    print=self.print,
                )
            if not skip:
                if not simulate:
                    move_action(fs, src_path, fs, dst_path)
                self.print("Renamed to %s" % file_desc(fs, dst_path))

        # the next action should work with the newly created copy
        return {
            "fs": fs,
            "fs_path": dst_path,
        }

    def __str__(self) -> str:
        return "Move(dest=%s, conflict_mode=%s)" % (self.dest, self.conflict_mode)
