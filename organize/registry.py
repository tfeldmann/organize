from __future__ import annotations

from typing import Dict, Type

from . import actions, filters
from .action import Action
from .filter import Filter

FILTERS: Dict[str, Type[Filter]] = dict()
ACTIONS: Dict[str, Type[Action]] = dict()


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


# Register filters and actions
for x in filters.ALL:
    register_filter(x)
for x in actions.ALL:
    register_action(x)
