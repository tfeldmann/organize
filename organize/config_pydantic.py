from rich import print
from enum import Enum
from fs.base import FS
from typing import List, Union
from typing_extensions import Annotated, Literal
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


DEFAULT_SYSTEM_EXCLUDE_FILES = ["asd"]
DEFAULT_SYSTEM_EXCLUDE_DIRS = [".git"]


class Location(BaseModel):
    path: str
    max_depth: Union[int, None] = None
    search: LocationSearchMethod = LocationSearchMethod.depth
    exclude_files: List[str] = Field(default_factory=list)
    exclude_dirs: List[str] = Field(default_factory=list)
    system_exclude_files: List[str] = Field(
        default_factory=lambda: DEFAULT_SYSTEM_EXCLUDE_FILES
    )
    system_exclude_dirs: List[str] = Field(
        default_factory=lambda: DEFAULT_SYSTEM_EXCLUDE_DIRS
    )
    filter: List[str] = Field(default_factory=list)
    filter_dirs: List[str] = Field(default_factory=list)
    ignore_errors: bool = False
    filesystem: Union[str, FS] = "."

    @validator(
        "exclude_files",
        "exclude_dirs",
        "system_exclude_files",
        "system_exclude_dirs",
        pre=True,
    )
    def ensure_set(cls, value):
        if isinstance(value, str):
            return set([value])
        return value


# FILTER

FilterType = str

# ACTIONS


class Action(BaseModel):
    class Meta:
        accepts_positional_arg = None

    def __init__(self, *args, **kwargs) -> None:
        if self.Meta.accepts_positional_arg and len(args) == 1:
            kwargs[self.Meta.accepts_positional_arg] = args[0]
            super().__init__(**kwargs)
            return
        super().__init__(*args, **kwargs)

    @root_validator(pre=True)
    def handle_single_str(cls, value):
        if "__non_dict_arg__" in value:
            param = cls.Meta.accepts_positional_arg
            if not param:
                raise ValueError("Non-dict arguments are not accepted")
            param_val = value.pop("__non_dict_arg__")
            return {param: param_val, **value}
        return value


class ConflictOptions(str, Enum):
    rename_new = "rename_new"
    overwrite = "overwrite"


class Move(Action):
    name: Literal["move"] = "move"

    dest: str
    on_conflict: ConflictOptions = ConflictOptions.rename_new
    rename_template: str = "{name} {counter}{extension}"
    filesystem: Union[None, str] = None

    class Meta:
        accepts_positional_arg = "dest"


class Copy(Action):
    name: Literal["copy"] = "copy"

    dest: str
    on_conflict: str = "rename_new"
    rename_template: str = "{name} {counter}{extension}"
    filesystem: Union[None, str] = None


## -- end actions

ActionType = Union[
    Action,
    Annotated[
        Union[Move, Copy],
        Field(discriminator="name"),
    ],
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
    enabled: bool = Field(True, repr=False)
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
        return value

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
    import sys, inspect

    sys.exit()

    x = Rule.parse_obj(
        {
            "locations": [{"path": "."}],
            "actions": [{"move": "asd"}],
        }
    )
    for action in x.actions:
        print(action)

    print(x)
    print(x.json())

    print(
        Rule(
            locations=Location(path="asd", exclude_dirs="asd"),
            actions=[Move(dest="asd"), {"move": "test"}],
            filters=[],
            targets="dirs",
        ).dict()
    )
