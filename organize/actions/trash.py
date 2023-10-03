from typing import ClassVar

from pydantic.dataclasses import dataclass

from organize.action import ActionConfig
from organize.output import Output
from organize.resource import Resource


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
        from send2trash import send2trash

        output.msg(res=res, msg=f'Trash "{res.path}"', sender=self)
        if not simulate:
            send2trash(res.path)
