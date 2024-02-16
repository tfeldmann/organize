from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, NamedTuple, Protocol, runtime_checkable

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
    def __init__(self, *args, **kwargs) -> None:
        # allow any amount of args / kwargs for BaseModel and dataclasses.
        ...
