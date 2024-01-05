from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional, Set

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .action import Action
from .filter import All, Any, Filter, HasFilterPipeline, Not
from .location import Location
from .output import Output
from .registry import action_by_name, filter_by_name
from .resource import Resource
from .template import render
from .utils import ReportSummary
from .validators import FlatList, flatten
from .walker import Walker

FilterMode = Literal["all", "any", "none"]


def action_from_dict(d: Dict) -> Action:
    """
    :param d:
        A dict in the forms of
        { "action_name": None }
        { "action_name": "value" }
        { "action_name": {"param": "value"} }
    :returns:
        An instantiated action.
    """
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


def filter_from_dict(d: Dict) -> Filter:
    """
    :param d:
        A dict in the forms of ("not" prefix is optional)
        { "[not] filter_name": None }
        { "[not] filter_name": "value" }
        { "[not] filter_name": {"param": "value"} }
    :returns: An instantiated filter.
    """
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


def filter_pipeline(
    filters: Iterable[Filter],
    filter_mode: FilterMode,
    res: Resource,
    output: Output,
) -> bool:
    collection: HasFilterPipeline
    if filter_mode == "all":
        collection = All(*filters)
    elif filter_mode == "any":
        collection = Any(*filters)
    elif filter_mode == "none":
        collection = All(*[Not(x) for x in filters])
    else:
        raise ValueError(f"Unknown filter mode {filter_mode}")
    return collection.pipeline(res, output=output)


def action_pipeline(
    actions: Iterable[Action],
    res: Resource,
    simulate: bool,
    output: Output,
) -> Iterable[Action]:
    for action in actions:
        try:
            yield action
            action.pipeline(res=res, simulate=simulate, output=output)
        except StopIteration:
            break


class Rule(BaseModel):
    name: Optional[str] = None
    enabled: bool = True
    targets: Literal["files", "dirs"] = "files"
    locations: FlatList[Location] = Field(default_factory=list)
    subfolders: bool = False
    tags: Set[str] = Field(default_factory=set)
    filters: List[Filter] = Field(default_factory=list)
    filter_mode: FilterMode = "all"
    actions: List[Action] = Field(..., min_length=1)

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    @field_validator("locations", mode="before")
    def validate_locations(cls, locations):
        if locations is None:
            return []
        locations = flatten(locations)
        result = []
        for x in locations:
            if isinstance(x, str):
                x = {"path": x}
            result.append(x)
        return result

    @field_validator("filters", mode="before")
    def validate_filters(cls, filters):
        result = []
        filters = flatten(filters)
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
        actions = flatten(actions)
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

    @model_validator(mode="after")
    def validate_target_support(self) -> "Rule":
        # standalone mode
        if not self.locations:
            if self.filters:
                raise ValueError("Filters are present but no locations are given!")
            for action in self.actions:
                if not action.action_config.standalone:
                    raise ValueError(
                        f'Action "{action.action_config.name}" does not support '
                        "standalone mode (no rule.locations specified)."
                    )
        # targets dirs
        if self.targets == "dirs":
            for filter in self.filters:
                if not filter.filter_config.dirs:
                    raise ValueError(
                        f'Filter "{filter.filter_config.name}" does not support '
                        "folders (targets: dirs)"
                    )
            for action in self.actions:
                if not action.action_config.dirs:
                    raise ValueError(
                        f'Action "{action.action_config.name}" does not support '
                        "folders (targets: dirs)"
                    )
        # targets files
        elif self.targets == "files":
            for filter in self.filters:
                if not filter.filter_config.files:
                    raise ValueError(
                        f'Filter "{filter.filter_config.name}" does not support '
                        "files (targets: files)"
                    )
            for action in self.actions:
                if not action.action_config.files:
                    raise ValueError(
                        f'Action "{action.action_config.name}" does not support '
                        "files (targets: files)"
                    )
        else:
            raise ValueError(f"Unknown target: {self.targets}")

        return self

    def walk(self, rule_nr: int = 0):
        for location in self.locations:
            # instantiate the filesystem walker
            exclude_files = location.system_exclude_files | location.exclude_files
            exclude_dirs = location.system_exclude_dirs | location.exclude_dirs
            if location.max_depth == "inherit":
                max_depth = None if self.subfolders else 0
            else:
                max_depth = location.max_depth

            walker = Walker(
                min_depth=location.min_depth,
                max_depth=max_depth,
                filter_dirs=location.filter_dirs,
                filter_files=location.filter,
                method="breadth",
                exclude_dirs=exclude_dirs,
                exclude_files=exclude_files,
            )

            # whether to walk dirs or files
            _walk_funcs = {
                "files": walker.files,
                "dirs": walker.dirs,
            }
            for loc_path in location.path:
                expanded_path = render(loc_path)
                for path in _walk_funcs[self.targets](expanded_path):
                    yield Resource(
                        path=Path(path),
                        basedir=Path(expanded_path),
                        rule=self,
                        rule_nr=rule_nr,
                    )

    def execute(
        self, *, simulate: bool, output: Output, rule_nr: int = 0
    ) -> ReportSummary:
        if not self.enabled:
            return ReportSummary()

        # standalone mode
        if not self.locations:
            res = Resource(path=None, rule_nr=rule_nr)
            try:
                for action in action_pipeline(
                    actions=self.actions,
                    res=res,
                    simulate=simulate,
                    output=output,
                ):
                    pass
                return ReportSummary(success=1)
            except Exception as e:
                output.msg(
                    res=res,
                    msg=str(e),
                    level="error",
                    sender=action,
                )
                # logging.exception(e)
                return ReportSummary(errors=1)

        # normal mode
        summary = ReportSummary()
        skip_pathes: Set[Path] = set()
        for res in self.walk(rule_nr=rule_nr):
            if res.path in skip_pathes:
                continue
            result = filter_pipeline(
                filters=self.filters,
                filter_mode=self.filter_mode,
                res=res,
                output=output,
            )
            if result:
                try:
                    for action in action_pipeline(
                        actions=self.actions,
                        res=res,
                        simulate=simulate,
                        output=output,
                    ):
                        pass
                    skip_pathes = skip_pathes.union(res.walker_skip_pathes)
                    summary.success += 1
                except Exception as e:
                    output.msg(
                        res=res,
                        msg=str(e),
                        level="error",
                        sender=action,
                    )
                    # logging.exception(e)
                    summary.errors += 1
        return summary
