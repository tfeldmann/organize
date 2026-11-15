from __future__ import annotations

from . import actions, filters
from .action import Action
from .filter import Filter

FILTERS: dict[str, type[Filter]] = dict()
ACTIONS: dict[str, type[Action]] = dict()


def register_filter(filter: type[Filter], force: bool = False):
    name = filter.filter_config.name
    if not force and name in FILTERS:
        raise ValueError(f'"{name}" is already registered for filter {FILTERS[name]}')
    FILTERS[name.lower()] = filter


def filter_by_name(name: str) -> type[Filter]:
    try:
        return FILTERS[name.lower()]
    except KeyError as e:
        raise ValueError(f'Unknown filter: "{name}"') from e


def register_action(action: type[Action], force: bool = False):
    name = action.action_config.name
    if not force and name in ACTIONS:
        raise ValueError(f'"{name}" is already registered for action {ACTIONS[name]}')
    ACTIONS[name.lower()] = action


def action_by_name(name: str) -> type[Action]:
    try:
        return ACTIONS[name.lower()]
    except KeyError as e:
        raise ValueError(f'Unknown action: "{name}"') from e


# Register filters and actions
for _filter in filters.ALL:
    register_filter(_filter)  # type: ignore
for _action in actions.ALL:
    register_action(_action)
