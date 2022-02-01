import logging
from typing import Callable

from fs.base import FS
from fs.copy import copy_dir, copy_file
from fs.path import basename, dirname, join
from schema import Optional, Or

from organize.utils import Template, open_fs_or_sim, resource_description

from .action import Action
from .utils import CONFLICT_OPTIONS, resolve_overwrite_conflict

logger = logging.getLogger(__name__)


class Copy(Action):

    """Copy a file or dir to a new location.

    If the specified path does not exist it will be created.

    Args:
        dest (str):
            The destination where the file / dir should be copied to.
            If `dest` ends with a slash, it is assumed to be a target directory
            and the file / dir will be copied into `dest` and keep its name.

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

    The next action will work with the created copy.
    """

    name = "copy"
    arg_schema = Or(
        str,
        {
            "dest": str,
            Optional("on_conflict"): Or(*CONFLICT_OPTIONS),
            Optional("rename_template"): str,
            Optional("filesystem"): str,
        },
    )

    def __init__(
        self,
        dest: str,
        on_conflict="rename_new",
        rename_template="{name} {counter}{extension}",
        filesystem=None,
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

        dst_path = self.dest.render(**args)
        # if the destination ends with a slash we assume the name should not change
        if dst_path.endswith(("\\", "/")):
            dst_path = join(dst_path, basename(src_path))

        if self.filesystem:
            dst_fs_ = self.filesystem
            # render if we have a template
            if isinstance(dst_fs_, str):
                dst_fs_ = Template.from_string(dst_fs_).render(**args)
            dst_fs = open_fs_or_sim(
                dst_fs_,
                writeable=True,
                create=True,
                simulate=simulate,
            )
            dst_path = dst_path
        else:
            dst_fs = open_fs_or_sim(
                dirname(dst_path),
                writeable=True,
                create=True,
                simulate=simulate,
            )
            dst_path = basename(dst_path)

        copy_action: Callable[[FS, str, FS, str], None]
        if src_fs.isdir(src_path):
            copy_action = copy_dir
        elif src_fs.isfile(src_path):
            copy_action = copy_file

        skip = False
        if dst_fs.exists(dst_path):
            self.print(
                '%s already exists (conflict mode is "%s").'
                % (resource_description(dst_fs, dst_path), self.conflict_mode)
            )
            dst_fs, dst_path, skip = resolve_overwrite_conflict(
                src_fs=src_fs,
                src_path=src_path,
                dst_fs=dst_fs,
                dst_path=dst_path,
                conflict_mode=self.conflict_mode,
                rename_template=self.rename_template,
                simulate=simulate,
                print=self.print,
            )
        if not skip:
            if not simulate:
                dst_fs.makedirs(dirname(dst_path), recreate=True)
                copy_action(src_fs, src_path, dst_fs, dst_path)
            self.print("Copied to %s" % resource_description(dst_fs, dst_path))

        # the next action should work with the newly created copy
        return {
            "fs": dst_fs,
            "fs_path": dst_path,
        }

    def __str__(self) -> str:
        return "Copy(dest=%s, conflict_mode=%s)" % (self.dest, self.conflict_mode)
