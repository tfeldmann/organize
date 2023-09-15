import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Union

from pydantic import ConfigDict, Field, field_validator
from pydantic.dataclasses import dataclass

from .action import Action
from .filter import Filter, Not
from .location import Location
from .registry import get_action, get_filter

logger = logging.getLogger(__name__)

rule_count = 0


def rule_name():
    global rule_count
    rule_count += 1
    return "Unnamed rule %s" % rule_count


class FilterMode(str, Enum):
    ALL = "all"
    ANY = "any"
    NONE = "none"


class RuleTarget(str, Enum):
    DIRS = "dirs"
    FILES = "files"


def action_from_dict(d):
    if not len(d.keys()) == 1:
        raise ValueError("Action definition must have only one key")
    name, value = next(iter(d.items()))
    ActionCls = get_action(name)
    if value is None:
        return ActionCls()
    elif isinstance(value, dict):
        return ActionCls(**value)
    else:
        return ActionCls(value)


def filter_from_dict(d: Dict):
    if not len(d.keys()) == 1:
        raise ValueError("Filter definition must have a single key")
    name, value = next(iter(d.items()))

    # check for "not" in filter key
    invert_filter = False
    if name.startswith("not "):
        name = name[4:]
        invert_filter = True

    FilterCls = get_filter(name)

    # instantiate
    if value is None:
        inst = FilterCls()
    elif isinstance(value, dict):
        inst = FilterCls(**value)
    else:
        inst = FilterCls(value)

    return Not(inst) if invert_filter else inst


@dataclass(kw_only=True, config=ConfigDict(extra="forbid"))
class Rule:
    name: Union[str, None] = Field(default_factory=rule_name)
    enabled: bool = True
    targets: RuleTarget = RuleTarget.FILES
    locations: List[Location] = Field(default_factory=list)
    subfolders: bool = False
    tags: List[str] = Field(default_factory=list)
    filters: List[Filter] = Field(default_factory=list)
    filter_mode: FilterMode = FilterMode.ALL
    actions: List[Action] = Field(..., min_items=1)

    @field_validator("locations", pre=True)
    def validate_locations(cls, v):
        if v is None:
            raise ValueError("Location cannot be empty")
        if isinstance(v, str):
            v = {"path": v}
        if not isinstance(v, list):
            v = [v]
        return v

    @field_validator("filters", mode="before")
    def validate_filters(cls, filters):
        result = []
        for x in filters:
            # make sure "- extension" becomes "- extension:"
            if isinstance(x, str):
                x = {x: None}
            # create instance from dict
            if isinstance(x, dict):
                result.append(filter_from_dict(x))
            # other instances
            else:
                result.append(x)
        return result

    @field_validator("actions", mode="before")
    def validate_actions(cls, actions):
        result = []
        for x in actions:
            # make sure "- extension" becomes "- extension:"
            if isinstance(x, str):
                x = {x: None}
            # create instance from dict
            if isinstance(x, dict):
                result.append(action_from_dict(x))
            # other instances
            else:
                result.append(x)
        return result

    def walk(self, working_dir: Union[Path, str] = "."):
        """
        Walk all given locations and yield the pathes
        """
        for location in self.locations:
            # instantiate the fs walker
            exclude_files = location.system_exclude_files + location.exclude_files
            exclude_dirs = location.system_exclude_dirs + location.exclude_dirs
            if location.max_depth == "inherit":
                max_depth = None if self.subfolders else 0
            else:
                max_depth = location.max_depth

            from .fs import Walker

            walker = Walker(
                min_depth=0,
                max_depth=max_depth,
                filter_dirs=location.filter_dirs,
                filter_files=location.filter,
                method=location.search,
                exclude_dirs=exclude_dirs,
                exclude_files=exclude_files,
            )

            # whether to walk dirs or files
            _walk_funcs = {
                RuleTarget.FILES: walker.files,
                RuleTarget.DIRS: walker.dirs,
            }
            walk_func = _walk_funcs[self.targets]

            for resource in walk_func(location.path):
                yield {
                    "working_dir": working_dir,
                }
