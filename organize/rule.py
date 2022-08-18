from enum import Enum
from typing import List, Union

from pydantic import BaseModel, Field, validator
from typing_extensions import Annotated

from .location import Location
from .pydantic_actions import Action, Copy, Move


def convert_to_list(cls, v):
    if not v:
        return []
    if isinstance(v, str):
        return v.split()
    return v


def normalize_to_list(field_name: str):
    return validator(field_name, allow_reuse=True, pre=True)(convert_to_list)


ActionType = Union[
    Action,
    Annotated[
        Union[Move, Copy],
        Field(discriminator="name"),
    ],
]
FilterType = str


class RuleFilterMode(str, Enum):
    all = "all"
    any = "any"
    none = "none"


class RuleTarget(str, Enum):
    dirs = "dirs"
    files = "files"


class Rule(BaseModel):
    name: str = "Rule"
    enabled: bool = Field(True, repr=False)
    subfolders: bool = False
    filter_mode: RuleFilterMode = RuleFilterMode.all
    targets: RuleTarget = RuleTarget.files
    locations: List[Location]
    actions: List[ActionType]
    filters: List[FilterType] = Field(default_factory=list)

    class Config:
        extra = "forbid"

    @validator("locations", pre=True)
    def validate_locations(cls, v):
        if not v:
            raise ValueError("Location cannot be empty")
        if not isinstance(v, list):
            v = [v]
        return v

    @validator("actions", pre=True, each_item=True)
    def action_rewriter(cls, value):
        if isinstance(value, dict):
            name = list(value.keys())[0]
            args = value[name]
            # if a single str is given as argument we handle this in the specific
            # action class
            if not isinstance(args, dict):
                return {"name": name, "__positional_arg__": args}
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
