from __future__ import annotations

from typing import Dict, Type

from pydantic import ConfigDict, validate_call

from . import actions, filters
from .action import Action
from .filter import Filter

FILTERS: Dict[str, Type[Filter]] = dict()
ACTIONS: Dict[str, Type[Action]] = dict()


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def register_filter(filter: Type[Filter], force: bool = False):
    name = filter.filter_config.name
    if not force and name in FILTERS:
        raise ValueError(f'"{name}" is already registered for filter {FILTERS[name]}')
    FILTERS[name] = filter


def filter_by_name(name: str) -> Type[Filter]:
    try:
        return FILTERS[name]
    except KeyError as e:
        raise ValueError(f'Unknown filter: "{name}"') from e


def name_for_filter(filter: Type[Filter]):
    for name, entry in FILTERS.items():
        if entry == filter:
            return name
    raise ValueError(f'Unknown filter type "{filter}"')


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def register_action(action: Type[Action], force: bool = False):
    name = action.action_config.name
    if not force and name in ACTIONS:
        raise ValueError(f'"{name}" is already registered for action {ACTIONS[name]}')
    ACTIONS[name] = action


def action_by_name(name: str) -> Type[Action]:
    try:
        return ACTIONS[name]
    except KeyError as e:
        raise ValueError(f'Unknown action: "{name}"') from e


def name_for_action(action: Type[Action]):
    for name, entry in ACTIONS.items():
        if entry == action:
            return name
    raise ValueError(f'Unknown action type "{action}"')


# Filters
register_filter(filters.Extension)
register_filter(filters.Name)

# Actions
register_action(actions.Echo)
