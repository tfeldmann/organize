from __future__ import annotations

import shutil
from typing import TYPE_CHECKING, ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.action import ActionConfig

if TYPE_CHECKING:
    from pathlib import Path

    from organize.output import Output
    from organize.resource import Resource


def delete(path: Path):
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


@dataclass(config=ConfigDict(extra="forbid"))
class Delete:
    """
    Delete a file from disk.

    Deleted files have no recovery option!
    Using the `Trash` action is strongly advised for most use-cases!
    """

    action_config: ClassVar[ActionConfig] = ActionConfig(
        name="delete",
        standalone=False,
        files=True,
        dirs=True,
    )

    def pipeline(self, res: Resource, output: Output, simulate: bool):
        assert res.path is not None, "Does not support standalone mode"
        output.msg(res=res, msg=f"Deleting {res.path}", sender=self)
        if not simulate:
            delete(res.path)
        res.path = None
