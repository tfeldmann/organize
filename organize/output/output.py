from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Protocol, runtime_checkable

if TYPE_CHECKING:
    from pathlib import Path

    from organize.resource import Resource

    from ._sender import SenderType


Level = Literal["info", "warn", "error"]


@runtime_checkable
class Output(Protocol):
    """
    The protocol all of organize's outputs must adhere to.
    """

    def start(
        self,
        simulate: bool,
        config_path: Optional[Path],
        working_dir: Path,
    ) -> None: ...

    def msg(
        self,
        res: Resource,
        msg: str,
        sender: SenderType,
        level: Level = "info",
    ) -> None: ...

    def confirm(
        self,
        res: Resource,
        msg: str,
        default: bool,
        sender: SenderType,
    ) -> bool: ...

    def end(self, success_count: int, error_count: int) -> None: ...
