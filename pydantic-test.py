# https://rjsf-team.github.io/react-jsonschema-form/

from rich import print
from pydantic import BaseModel, validator
from typing import List, Optional, Union
from enum import Enum


def expand_location(x: Union[str, list]):
    if isinstance(x, str):
        # location is given as single string
        x = {"path": x}
    return x


class FilterModeEnum(str, Enum):
    all = "all"
    any = "any"
    none = "none"


class RuleTarget(str, Enum):
    dirs = "dirs"
    files = "files"


class LocationSearchMethod(str, Enum):
    depth = "depth"
    breadth = "breadth"


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


class ExtensionSchema(BaseModel):
    extension: List[str]

    @validator("extension", pre=True)
    def convert_to_list(cls, v):
        if not v:
            return []
        if isinstance(v, str):
            return v.split()
        return v


class SizeSchema(BaseModel):
    size: int


x = (ExtensionSchema, SizeSchema)
FILTER_NAMES = ["size", "extension"]
Filters = Union[x]
Actions = None


class Rule(BaseModel):
    name: str = "Rule"
    enabled: bool = True
    subfolders: bool = False
    filter_mode: FilterModeEnum = FilterModeEnum.all
    targets: RuleTarget = RuleTarget.files

    locations: List[Location]
    actions: Actions
    filters: Optional[List[Filters]]

    class Config:
        extra = "forbid"

    @validator("filters", pre=True, each_item=True)
    def validate_filters(cls, v):
        if isinstance(v, str):
            v = {v: None}
        if not isinstance(v, dict):
            raise ValueError("Filter cannot be None")
        if len(v.keys()) != 1:
            keys = ", ".join(list(v.keys()))
            raise ValueError(
                "Filter definitions must have the filter name as the only key. (Keys: %s)"
                % keys
            )
        if list(v.keys())[0] not in FILTER_NAMES:
            raise ValueError('Unknown filter: "%s"' % list(v.keys())[0])
        return v

    @validator("locations", pre=True)
    def validate_locations(cls, v):
        if not isinstance(v, list):
            v = [v]
        v = [expand_location(x) for x in v]
        return v


class Config(BaseModel):
    rules: List[Rule]

    class Config:
        title = "organize config file"


config = {
    "rules": [
        {
            "actions": None,
            "filters": [{"size": 1}],
            "filter_mode": "all",
            "locations": "test",
        },
        {
            "actions": None,
            "filters": [
                "extension",
                {"extension": "asd"},
                {"extension": "asd asd"},
                {"size": 100},
                None,
            ],
            "filter_mode": "all",
            "locations": [
                {"path": "~/Desktop"},
                "test",
            ],
        },
    ]
}

conf = Config(**config)
print(conf.dict())
# print(conf)
# print(Config.schema_json(indent=4))
