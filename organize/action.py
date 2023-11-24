from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, NamedTuple

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from .output import Output
    from .resource import Resource


class ActionConfig(NamedTuple):
    name: str
    standalone: bool
    files: bool
    dirs: bool


@runtime_checkable
class HasActionConfig(Protocol):
    action_config: ClassVar[ActionConfig]


class HasActionPipeline(Protocol):
    def pipeline(self, res: Resource, output: Output, simulate: bool):
        ...


@runtime_checkable
class Action(HasActionConfig, HasActionPipeline, Protocol):
    pass
