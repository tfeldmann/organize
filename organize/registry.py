from typing import Dict, Type

from pydantic import ConfigDict, validate_call

from .action import Action
from .filter import Filter

FILTERS: Dict[str, Filter] = dict()
ACTIONS: Dict[str, Action] = dict()


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def register_filter(filter: Type[Filter], name: str, force: bool = False):
    if not force and name in FILTERS:
        raise ValueError(f'"{name}" is already registered for filter {FILTERS[name]}')
    FILTERS[name] = filter


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def register_action(action: Type[Action], name: str, force: bool = False):
    if not force and name in ACTIONS:
        raise ValueError(f'"{name}" is already registered for action {ACTIONS[name]}')
    ACTIONS[name] = action


def get_filter(name: str) -> Type[Filter]:
    try:
        return FILTERS[name]
    except KeyError as e:
        raise ValueError(f'Unknown filter: "{name}"') from e


def get_action(name: str) -> Type[Action]:
    try:
        return ACTIONS[name]
    except KeyError as e:
        raise ValueError(f'Unknown action: "{name}"') from e
