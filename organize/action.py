from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from .output import Output
    from .resource import Resource


@runtime_checkable
class Action(Protocol):
    def pipeline(self, res: Resource, output: Output, simulate: bool) -> dict:
        ...
