from pathlib import Path
from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource


def trash(path: Path):
    from send2trash import send2trash

    send2trash(path)


@dataclass(config=ConfigDict(coerce_numbers_to_str=True, extra="forbid"))
class Trash:
    """Move a file or dir into the trash."""

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="trash",
        standalone=False,
        files=True,
        dirs=True,
    )

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        assert res.path is not None, "Does not support standalone mode"
        output.msg(res=res, msg=f'Trash "{res.path}"', sender=self)
        if not simulate:
            trash(res.path)
