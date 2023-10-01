from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, ClassVar

from pydantic.dataclasses import dataclass

from organize.action import ActionConfig

if TYPE_CHECKING:
    from organize.output import Output
    from organize.resource import Resource


@dataclass
class Delete:

    """
    Delete a file from disk.

    Deleted files have no recovery option!
    Using the `Trash` action is strongly advised for most use-cases!
    """

    action_config: ClassVar = ActionConfig(
        name="delete",
        standalone=False,
        files=True,
        dirs=True,
    )

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        output.msg(res=res, msg=f"Deleting {res.path}", sender=self)
        if not simulate:
            if res.is_dir():
                shutil.rmtree(res.path)
            else:
                res.path.unlink()
