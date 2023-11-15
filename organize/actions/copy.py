import shutil
from typing import ClassVar, Literal

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template

from .common.conflict import ConflictMode, resolve_conflict
from .common.target_path import prepare_target_path


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Copy:

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

        autodetect_folder (bool) = True
            In case you forget the ending slash "/" to indicate copying into a folder
            this settings will handle targets without a file extension as folders.
            If you really mean to copy to a file without file extension, set this to
            false.

        continue_with (str) = "copy" | "original"
            Continue the next action either with the path to the copy or the path the
            original.

    The next action will work with the created copy.
    """

    dest: str
    on_conflict: ConflictMode = ConflictMode.RENAME_NEW
    rename_template: str = "{name} {counter}{extension}"
    autodetect_folder: bool = True
    continue_with: Literal["copy", "original"] = "copy"

    action_config: ClassVar = ActionConfig(
        name="copy",
        standalone=False,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self._dest = Template.from_string(self.dest)
        self._rename_template = Template.from_string(self.rename_template)

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        rendered = self._dest.render(**res.dict())

        # fully resolve the destination for folder targets and prepare the folder
        # structure
        dst = prepare_target_path(
            src_name=res.path.name,
            dst=rendered,
            autodetect_folder=self.autodetect_folder,
            simulate=simulate,
        )

        # Resolve conflicts before copying the file to the destination
        skip_action, dst = resolve_conflict(
            dst=dst,
            res=res,
            conflict_mode=self.on_conflict,
            rename_template=self._rename_template,
            simulate=simulate,
            output=output,
        )

        if skip_action:
            return

        output.msg(res=res, msg=f"Copy to {dst}", sender=self)
        if not simulate:
            if res.is_dir():
                shutil.copytree(src=res.path, dst=dst)
            else:
                shutil.copy2(src=res.path, dst=dst)

        # continue with either the original path or the path to the copy
        if self.continue_with == "copy":
            res.path = dst
