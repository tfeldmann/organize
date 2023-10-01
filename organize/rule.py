import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from pydantic import ConfigDict, Field, field_validator
from pydantic.dataclasses import dataclass
from rich import print

from .action import Action
from .filter import All, Filter, Not
from .location import Location
from .registry import action_by_name, filter_by_name
from .resource import Resource


def action_from_dict(d):
    if not len(d.keys()) == 1:
        raise ValueError("Action definition must have only one key")
    name, value = next(iter(d.items()))
    ActionCls = action_by_name(name)
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

    FilterCls = filter_by_name(name)

    # instantiate
    if value is None:
        inst = FilterCls()
    elif isinstance(value, dict):
        inst = FilterCls(**value)
    else:
        inst = FilterCls(value)

    return Not(inst) if invert_filter else inst


class FilterMode(str, Enum):
    ALL = "all"
    ANY = "any"
    NONE = "none"


class RuleTarget(str, Enum):
    DIRS = "dirs"
    FILES = "files"


@dataclass(
    kw_only=True,
    config=ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
    ),
)
class Rule:
    name: Optional[str] = None
    enabled: bool = True
    targets: RuleTarget = RuleTarget.FILES
    locations: List[Location] = Field(default_factory=list)
    subfolders: bool = False
    tags: Set[str] = Field(default_factory=set)
    filters: List[Filter] = Field(default_factory=list)
    filter_mode: FilterMode = FilterMode.ALL
    actions: List[Action] = Field(..., min_length=1)

    @field_validator("locations", mode="before")
    def validate_locations(cls, locations):
        if locations is None:
            raise ValueError("Location cannot be empty")
        if not isinstance(locations, list):
            locations = [locations]
        result = []
        for x in locations:
            if isinstance(x, str):
                x = {"path": x}
            result.append(x)
        return result

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
        for location in self.locations:
            # instantiate the fs walker
            exclude_files = location.system_exclude_files + location.exclude_files
            exclude_dirs = location.system_exclude_dirs + location.exclude_dirs
            if location.max_depth == "inherit":
                max_depth = None if self.subfolders else 0
            else:
                max_depth = location.max_depth

            from .walker import Walker

            walker = Walker(
                min_depth=0,
                max_depth=max_depth,
                filter_dirs=location.filter_dirs,
                filter_files=location.filter,
                method="breadth",
                exclude_dirs=exclude_dirs,
                exclude_files=exclude_files,
            )

            # whether to walk dirs or files
            _walk_funcs = {
                RuleTarget.FILES: walker.files,
                RuleTarget.DIRS: walker.dirs,
            }
            walk_func = _walk_funcs[self.targets]

            for path in walk_func(location.path):
                yield Resource(path=Path(path), rule=self, basedir=location.path)

    def execute(self, *, simulate: bool):
        from .output import JSONL as Output

        output = Output()
        output.start(simulate=simulate)
        for res in self.walk():
            result = All(*self.filters).pipeline(res, output=output)  # TODO: Any
            if result:
                try:
                    for action in self.actions:
                        action.pipeline(res, simulate=simulate, output=output)
                except Exception as e:
                    output.msg(res=res, msg=str(e), level="error")
                    logging.exception(e)
