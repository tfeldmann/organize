from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Protocol, Union

if TYPE_CHECKING:
    from organize.action import Action
    from organize.filter import Filter
    from organize.resource import Resource


class Output(Protocol):
    def start(self, simulate: bool, config_path: Optional[str] = None):
        ...

    def msg(
        self,
        res: Resource,
        msg: str,
        level: Literal["info", "warn", "error"] = "info",
        sender: Union[Filter, Action, str] = "",
    ):
        ...

    def confirm(self, res: Resource, msg: str) -> bool:
        ...

    def end(self, success_count: int, error_count: int):
        ...


def highlight_path(path: Path, base_style: str, item_style: str):
    return
