import logging
from typing import Callable

from fs import path
from fs.base import FS
from fs.move import move_dir, move_file
from pydantic import Field
from typing_extensions import Literal

from organize.utils import Template, safe_description

from .action import Action
from .common.conflict import ConflictOption, check_conflict

logger = logging.getLogger(__name__)


class Rename(Action):

    """Renames a file.

    Args:
        name (str):
            The new name for the file / dir.

        on_conflict (str):
            What should happen in case **dest** already exists.
            One of `skip`, `overwrite`, `trash`, `rename_new` and `rename_existing`.
            Defaults to `rename_new`.

        rename_template (str):
            A template for renaming the file / dir in case of a conflict.
            Defaults to `{name} {counter}{extension}`.

    The next action will work with the renamed file / dir.
    """

    name: Literal["rename"] = Field("rename", repr=False)

    new_name: str
    on_conflict: ConflictOption = ConflictOption.rename_new
    rename_template: str = "{name} {counter}{extension}"

    class ParseConfig:
        accepts_positional_arg = "new_name"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._new_name = Template.from_string(self.new_name)
        self._rename_template = Template.from_string(self.rename_template)

    def pipeline(self, args: dict, simulate: bool):
        fs = args["fs"]  # type: FS
        src_path = args["fs_path"]

        new_name = self._new_name.render(**args)
        if "/" in new_name:
            raise ValueError(
                "The new name cannot contain slashes. "
                "To move files or folders use `move`."
            )

        dst_path = path.join(path.dirname(src_path), new_name)

        if dst_path == src_path:
            self.print("Name did not change")
        else:
            move_action: Callable[[FS, str, FS, str], None]
            if fs.isdir(src_path):
                move_action = move_dir
            elif fs.isfile(src_path):
                move_action = move_file

            # check for conflicts
            skip, dst_path = check_conflict(
                src_fs=fs,
                src_path=src_path,
                dst_fs=fs,
                dst_path=dst_path,
                conflict_mode=self.conflict_mode,
                rename_template=self._rename_template,
                simulate=simulate,
                print=self.print,
            )

            if not skip:
                self.print("Rename to %s" % safe_description(fs, dst_path))
                if not simulate:
                    move_action(fs, src_path, fs, dst_path)

        # the next action should work with the renamed file
        return {
            "fs": fs,
            "fs_path": "./" + dst_path,
        }
