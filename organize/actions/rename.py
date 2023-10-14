from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template

from .common.conflict import ConflictMode


def rename(path: Path, name: str):
    raise NotImplementedError()


@dataclass
class Rename:

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

    new_name: str
    on_conflict: ConflictMode = ConflictMode.RENAME_NEW
    rename_template: str = "{name} {counter}{extension}"

    action_config: ClassVar = ActionConfig(
        name="rename",
        standalone=False,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self._new_name = Template.from_string(self.new_name)
        self._rename_template = Template.from_string(self.rename_template)

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        new_name = self._new_name.render(**res.dict())
        if "/" in new_name:
            raise ValueError(
                "The new name cannot contain slashes. "
                "To move files or folders use `move`."
            )
        raise NotImplementedError()
        # dst_path = path.join(path.dirname(src_path), new_name)

        # if dst_path == src_path:
        #     self.print("Name did not change")
        # else:
        #     move_action: Callable[[FS, str, FS, str], None]
        #     if fs.isdir(src_path):
        #         move_action = move_dir
        #     elif fs.isfile(src_path):
        #         move_action = move_file

        #     # check for conflicts
        #     skip, dst_path = check_conflict(
        #         src_fs=fs,
        #         src_path=src_path,
        #         dst_fs=fs,
        #         dst_path=dst_path,
        #         conflict_mode=self.conflict_mode,
        #         rename_template=self._rename_template,
        #         simulate=simulate,
        #         print=self.print,
        #     )

        #     if not skip:
        #         self.print("Rename to %s" % safe_description(fs, dst_path))
        #         if not simulate:
        #             move_action(fs, src_path, fs, dst_path)

        # # the next action should work with the renamed file
        # return {
        #     "fs": fs,
        #     "fs_path": "./" + dst_path,
        # }
