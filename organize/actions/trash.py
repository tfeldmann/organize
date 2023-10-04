from typing import TYPE_CHECKING, ClassVar

from pydantic.dataclasses import dataclass

from organize.action import ActionConfig

if TYPE_CHECKING:
    from pathlib import Path

    from organize.output import Output
    from organize.resource import Resource


def trash(path: Path):
    from send2trash import send2trash

    send2trash(path)


@dataclass
class Trash:

    """Move a file or dir into the trash."""

    action_config: ClassVar = ActionConfig(
        name="trash",
        standalone=False,
        files=True,
        dirs=True,
    )

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        output.msg(res=res, msg=f'Trash "{res.path}"', sender=self)
        if not simulate:
            trash(res.path)
