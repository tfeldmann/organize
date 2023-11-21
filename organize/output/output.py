from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Protocol, Union

if TYPE_CHECKING:
    from pathlib import Path

    from organize.action import Action
    from organize.filter import Filter
    from organize.resource import Resource


class Output(Protocol):
    """
    The protocol all of organize's outputs must adhere to.
    """

    def start(self, simulate: bool, config_path: Optional[Path] = None):
        ...

    def msg(
        self,
        res: Resource,
        msg: str,
        level: Literal["info", "warn", "error"] = "info",
        sender: Union[Filter, Action, str] = "",
    ) -> None:
        ...

    def confirm(
        self,
        res: Resource,
        msg: str,
        default: bool,
        sender: Union[Filter, Action, str] = "",
    ) -> bool:
        ...

    def end(self, success_count: int, error_count: int):
        ...
