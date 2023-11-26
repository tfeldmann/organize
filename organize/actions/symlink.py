from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template, render

from .common.conflict import ConflictMode, resolve_conflict
from .common.target_path import prepare_target_path


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Symlink:

    """Create a symbolic link.

    Args:
        dest (str):
            The symlink destination. If **dest** ends with a slash `/``, create the
            symlink in the given directory. Can contain placeholders.

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
    """

    dest: str
    on_conflict: ConflictMode = "rename_new"
    rename_template: str = "{name} {counter}{extension}"
    autodetect_folder: bool = True

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="symlink",
        standalone=False,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self._dest = Template.from_string(self.dest)
        self._rename_template = Template.from_string(self.rename_template)

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        assert res.path is not None, "Does not support standalone mode"
        rendered = render(self._dest, res.dict())
        dst = prepare_target_path(
            src_name=res.path.name,
            dst=rendered,
            autodetect_folder=self.autodetect_folder,
            simulate=simulate,
        )

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

        output.msg(res=res, msg=f"Creating symlink at {dst}", sender=self)
        res.walker_skip_pathes.add(dst)
        if not simulate:
            dst.symlink_to(target=res.path, target_is_directory=res.is_dir())
