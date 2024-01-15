from __future__ import annotations

from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template, render

from .common.conflict import ConflictMode, resolve_conflict


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Rename:

    """Renames a file.

    Attributes:
        new_name (str):
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
    on_conflict: ConflictMode = "rename_new"
    rename_template: str = "{name} {counter}{extension}"
    # TODO: keep_extension?

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="rename",
        standalone=False,
        files=True,
        dirs=True,
    )

    def __post_init__(self):
        self._new_name = Template.from_string(self.new_name)
        self._rename_template = Template.from_string(self.rename_template)

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        assert res.path is not None, "Does not support standalone mode"
        new_name = render(self._new_name, res.dict())
        if "/" in new_name:
            raise ValueError(
                "The new name cannot contain slashes. "
                "To move files or folders use `move`."
            )
        dst = res.path.with_name(new_name)
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

        output.msg(res=res, msg=f"Renaming to {new_name}", sender=self)
        if not simulate:
            res.path.rename(dst)
        res.path = dst
        res.walker_skip_pathes.add(dst)
