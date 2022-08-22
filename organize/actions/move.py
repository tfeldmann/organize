from typing import Callable, Union

import fs
from fs.base import FS
from fs.opener.errors import OpenerError
from typing_extensions import Literal

from organize.utils import SimulationFS, Template, safe_description

from ._conflict import ConflictOption, check_conflict, dst_from_options
from .action import Action


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

    name: Literal["move"] = "move"

    dest: str
    on_conflict: ConflictOption = ConflictOption.rename_new
    rename_template: str = "{name} {counter}{extension}"
    filesystem: Union[FS, str, None] = None

    _dest: Template
    _rename_template: Template

    class Config:
        accepts_positional_arg = "dest"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dest = Template.from_string(self.dest)
        self._rename_template = Template.from_string(self.rename_template)
        # self.filesystem = filesystem or self.Meta.default_filesystem

    def pipeline(self, args: dict, simulate: bool):
        src_fs = args["fs"]  # type: FS
        src_path = args["fs_path"]

        move_action: Callable[[FS, str, FS, str], None]
        if src_fs.isdir(src_path):
            move_action = fs.move.move_dir
        elif src_fs.isfile(src_path):
            move_action = fs.move.move_file

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
            dst_fs = fs.open_fs(dst_fs, create=False, writeable=True)
        except (fs.errors.CreateFailed, OpenerError):
            if not simulate:
                dst_fs = fs.open_fs(dst_fs, create=True, writeable=True)
            else:
                dst_fs = SimulationFS(dst_fs)

        if not skip:
            self.print("Move to %s" % safe_description(dst_fs, dst_path))
            if not simulate:
                dst_fs.makedirs(fs.path.dirname(dst_path), recreate=True)
                move_action(src_fs, src_path, dst_fs, dst_path)

        # the next action should work with the newly created copy
        return {
            "fs": dst_fs,
            "fs_path": dst_path,
        }
