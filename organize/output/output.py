from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Protocol

if TYPE_CHECKING:
    from pathlib import Path

    from organize.resource import Resource

    from ._sender import SenderType


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
        sender: SenderType = "",
    ) -> None:
        ...

    def confirm(
        self,
        res: Resource,
        msg: str,
        default: bool,
        sender: SenderType = "",
    ) -> bool:
        ...

    def end(self, success_count: int, error_count: int):
        ...
