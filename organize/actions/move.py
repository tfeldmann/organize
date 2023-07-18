from os.path import commonpath
from typing import Callable, Union

from fs import errors, open_fs
from fs.base import FS
from fs.copy import copy_file
from fs.errors import FSError
from fs.move import move_dir
from fs.opener import manage_fs
from fs.opener.errors import OpenerError
from fs.osfs import OSFS
from fs.path import dirname, frombase
from schema import Optional, Or

from organize.utils import SimulationFS, Template, safe_description

from ._conflict_resolution import CONFLICT_OPTIONS, check_conflict, dst_from_options
from .action import Action


# this is taken from my PR
def move_file_optimized(
    src_fs,
    src_path,
    dst_fs,
    dst_path,
    preserve_time=False,
    cleanup_dst_on_error=True,
):
    # type: (...) -> None
    """Move a file from one filesystem to another.

    Arguments:
        src_fs (FS or str): Source filesystem (instance or URL).
        src_path (str): Path to a file on ``src_fs``.
        dst_fs (FS or str): Destination filesystem (instance or URL).
        dst_path (str): Path to a file on ``dst_fs``.
        preserve_time (bool): If `True`, try to preserve mtime of the
            resources (defaults to `False`).
        cleanup_dst_on_error (bool): If `True`, tries to delete the file copied to
            ``dst_fs`` if deleting the file from ``src_fs`` fails (defaults to `True`).

    """
    with manage_fs(src_fs, writeable=True) as _src_fs:
        with manage_fs(dst_fs, writeable=True, create=True) as _dst_fs:
            if _src_fs is _dst_fs:
                # Same filesystem, may be optimized
                _src_fs.move(
                    src_path, dst_path, overwrite=True, preserve_time=preserve_time
                )
                return

            if _src_fs.hassyspath(src_path) and _dst_fs.hassyspath(dst_path):
                # if both filesystems have a syspath we create a new OSFS from a
                # common parent folder and use it to move the file.
                try:
                    src_syspath = _src_fs.getsyspath(src_path)
                    dst_syspath = _dst_fs.getsyspath(dst_path)
                    common = commonpath([src_syspath, dst_syspath])
                    if common:
                        rel_src = frombase(common, src_syspath)
                        rel_dst = frombase(common, dst_syspath)
                        with _src_fs.lock(), _dst_fs.lock():
                            with OSFS(common) as base:
                                base.move(rel_src, rel_dst, preserve_time=preserve_time)
                                return  # optimization worked, exit early
                except ValueError:
                    # This is raised if we cannot find a common base folder.
                    # In this case just fall through to the standard method.
                    pass

            # Standard copy and delete
            with _src_fs.lock(), _dst_fs.lock():
                copy_file(
                    _src_fs,
                    src_path,
                    _dst_fs,
                    dst_path,
                    preserve_time=preserve_time,
                )
                try:
                    _src_fs.remove(src_path)
                except FSError as e:
                    # if the source cannot be removed we delete the copy on the
                    # destination
                    if cleanup_dst_on_error:
                        _dst_fs.remove(dst_path)
                    raise e


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
        filesystem: Union[FS, str, None] = None,
    ) -> None:
        if on_conflict not in CONFLICT_OPTIONS:
            raise ValueError(
                f"on_conflict must be one of {', '.join(CONFLICT_OPTIONS)}"
            )

        self.dest = Template.from_string(dest)
        self.conflict_mode = on_conflict
        self.rename_template = Template.from_string(rename_template)
        self.filesystem = filesystem or self.Meta.default_filesystem

    def pipeline(self, args: dict, simulate: bool):
        src_fs = args["fs"]  # type: FS
        src_path = args["fs_path"]

        move_action: Callable[[FS, str, FS, str], None]
        if src_fs.isdir(src_path):
            move_action = move_dir
        elif src_fs.isfile(src_path):
            move_action = move_file_optimized

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
        except (errors.CreateFailed, OpenerError):
            if not simulate:
                dst_fs = open_fs(dst_fs, create=True, writeable=True)
            else:
                dst_fs = SimulationFS(dst_fs)

        if not skip:
            self.print(f"Move to {safe_description(dst_fs, dst_path)}")
            if not simulate:
                dst_fs.makedirs(dirname(dst_path), recreate=True)
                move_action(src_fs, src_path, dst_fs, dst_path)

        # the next action should work with the newly created copy
        return {
            "fs": dst_fs,
            "fs_path": dst_path,
        }

    def __str__(self) -> str:
        return f"Move(dest={self.dest}, conflict_mode={self.conflict_mode})"
