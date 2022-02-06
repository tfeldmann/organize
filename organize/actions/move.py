from typing import Callable, Union

from fs import open_fs
from fs import errors
from fs.base import FS
from fs.move import move_dir, move_file
from fs.path import dirname
from schema import Optional, Or

from organize.utils import Template, safe_description, SimulationFS

from .action import Action
from .copymove_utils import CONFLICT_OPTIONS, check_conflict, dst_from_options


class Move(Action):

    """Move a file to a new location.

    The file can also be renamed.
    If the specified path does not exist it will be created.

    If you only want to rename the file and keep the folder, it is
    easier to use the `rename` action.

    Args:
        dest (str):
            The destination where the file / dir should be moved to.
            If `dest` ends with a slash, it is assumed to be a target directory
            and the file / dir will be moved into `dest` and keep its name.

        on_conflict (str):
            What should happen in case **dest** already exists.
            One of `skip`, `overwrite`, `trash`, `rename_new` and `rename_existing`.
            Defaults to `rename_new`.

        rename_template (str):
            A template for renaming the file / dir in case of a conflict.
            Defaults to `{name} {counter}{extension}`.

        filesystem (str):
            (Optional) A pyfilesystem opener url of the filesystem you want to copy to.
            If this is not given, the local filesystem is used.

    The next action will work with the moved file / dir.
    """

    name = "move"
    arg_schema = Or(
        str,
        {
            "dest": str,
            Optional("on_conflict"): Or(*CONFLICT_OPTIONS),
            Optional("rename_template"): str,
            Optional("filesystem"): object,
        },
    )

    def __init__(
        self,
        dest: str,
        on_conflict="rename_new",
        rename_template="{name} {counter}{extension}",
        filesystem: Union[str, FS] = "",
    ) -> None:
        if on_conflict not in CONFLICT_OPTIONS:
            raise ValueError(
                "on_conflict must be one of %s" % ", ".join(CONFLICT_OPTIONS)
            )

        self.dest = Template.from_string(dest)
        self.conflict_mode = on_conflict
        self.rename_template = Template.from_string(rename_template)
        self.filesystem = filesystem

    def pipeline(self, args: dict, simulate: bool):
        src_fs = args["fs"]  # type: FS
        src_path = args["fs_path"]

        move_action: Callable[[FS, str, FS, str], None]
        if src_fs.isdir(src_path):
            move_action = move_dir
        elif src_fs.isfile(src_path):
            move_action = move_file

        dst_fs, dst_path = dst_from_options(
            src_path=src_path,
            dest=self.dest,
            filesystem=self.filesystem,
            args=args,
        )

        # check for conflicts
        skip, dst_path = check_conflict(
            src_fs=src_fs,
            src_path=src_path,
            dst_fs=dst_fs,
            dst_path=dst_path,
            conflict_mode=self.conflict_mode,
            rename_template=self.rename_template,
            simulate=simulate,
            print=self.print,
        )

        try:
            dst_fs = open_fs(dst_fs, create=False, writeable=True)
        except errors.CreateFailed:
            if not simulate:
                dst_fs = open_fs(dst_fs, create=True, writeable=True)
            else:
                dst_fs = SimulationFS(dst_fs)

        if not skip:
            self.print("Move to %s" % safe_description(dst_fs, dst_path))
            if not simulate:
                dst_fs.makedirs(dirname(dst_path), recreate=True)
                move_action(src_fs, src_path, dst_fs, dst_path)

        # the next action should work with the newly created copy
        return {
            "fs": dst_fs,
            "fs_path": dst_path,
        }

    def __str__(self) -> str:
        return "Move(dest=%s, conflict_mode=%s)" % (self.dest, self.conflict_mode)
