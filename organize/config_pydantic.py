from rich import print
from enum import Enum
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, root_validator, validator


class LocationSearchMethod(str, Enum):
    depth = "depth"
    breadth = "breadth"


class RuleFilterMode(str, Enum):
    all = "all"
    any = "any"
    none = "none"


class RuleTarget(str, Enum):
    dirs = "dirs"
    files = "files"


class BaseModel(PydanticBaseModel):
    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True


class Location(BaseModel):
    path: str
    max_depth: Optional[int] = None
    search: LocationSearchMethod = LocationSearchMethod.depth
    exclude_files: Union[None, str, List[str]]
    exclude_dirs: Union[None, str, List[str]]
    system_exclude_files: Union[None, str, List[str]]
    system_exclude_dirs: Union[None, str, List[str]]
    filter: Union[None, str, List[str]]
    filter_dirs: Union[None, str, List[str]]
    ignore_errors: bool = False
    filesystem: Optional[Union[str, object]]


# FILTER

FilterType = None

# ACTIONS


class Action(BaseModel):
    class Meta:
        param_for_single_str = None

    @root_validator(pre=True)
    def handle_single_str(cls, value):
        if "__non_dict_arg__" in value:
            param = cls.Meta.param_for_single_str
            if not param:
                raise ValueError("Non-dict arguments are not accepted")
            param_val = value.pop("__non_dict_arg__")
            return {param: param_val, **value}
        return value


class ConflictOptions(str, Enum):
    rename_new = "rename_new"
    overwrite = "overwrite"


class Move(Action):
    name: Literal["move"]

    dest: str
    on_conflict: ConflictOptions = ConflictOptions.rename_new
    rename_template: str = "{name} {counter}{extension}"
    filesystem: Union[None, str] = None

    class Meta:
        param_for_single_str = "dest"


class Copy(Action):
    name: Literal["copy"]

    dest: str
    on_conflict: str = "rename_new"
    rename_template: str = "{name} {counter}{extension}"
    filesystem: Union[None, str] = None


## -- end actions

ActionType = Annotated[
    Union[Move, Copy],
    Field(discriminator="name"),
]


def convert_to_list(cls, v):
    if not v:
        return []
    if isinstance(v, str):
        return v.split()
    return v


def normalize_to_list(field_name: str):
    return validator(field_name, allow_reuse=True, pre=True)(convert_to_list)


def expand_location(x: Union[str, list]):
    if isinstance(x, str):
        # location is given as single string
        x = {"path": x}
    return x


class Rule(BaseModel):
    name: str = "Rule"
    enabled: bool = True
    subfolders: bool = False
    filter_mode: RuleFilterMode = RuleFilterMode.all
    targets: RuleTarget = RuleTarget.files
    locations: List[Location]
    actions: List[ActionType]
    filters: List[FilterType] = Field(default_factory=list)

    @validator("locations", pre=True)
    def validate_locations(cls, v):
        if not v:
            raise ValueError("Location cannot be empty")
        if not isinstance(v, list):
            v = [v]
        v = [expand_location(x) for x in v]
        return v

    @validator("actions", pre=True, each_item=True)
    def action_rewriter(cls, value):
        if isinstance(value, dict):
            name = list(value.keys())[0]
            args = value[name]
            # if a single str is given as argument we handle this in the specific
            # action class
            if not isinstance(args, dict):
                return {"name": name, "__non_dict_arg__": args}
            return {"name": name, **args}
        raise ValueError("actions must be a list of dicts: %s" % value)

    @validator("filters", pre=True, each_item=True)
    def validate_filters(cls, v):
        if not v:
            raise ValueError("Filter cannot be empty")
        if isinstance(v, str):
            v = {v: None}
        if len(v.keys()) != 1:
            keys = ", ".join(list(v.keys()))
            raise ValueError(
                "Filter definitions must have a filter name as the only key. "
                "Found keys: %s" % keys
            )
        return v


class Config(BaseModel):
    rules: List[Rule]

    class Config:
        title = "organize config file"


if __name__ == "__main__":
    x = Rule.parse_obj(
        {
            "locations": [{"path": "."}],
            "actions": [{"move": "asd"}],
        }
    )
    for action in x.actions:
        print(action)

    print(x)
    print(x.dict())
