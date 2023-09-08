from pathlib import Path
from rich import print
from typing import List, Union, Literal
from pydantic.dataclasses import dataclass
from pydantic import Field, field_validator, ConfigDict
from enum import StrEnum
from itertools import count
from typing import ClassVar, NamedTuple

rule_count = count(start=1)


def rule_name():
    global rule_count
    return f"Unnamed rule {next(rule_count)}"


class FilterMode(StrEnum):
    ALL = "all"
    ANY = "any"
    NONE = "none"


class RuleTarget(StrEnum):
    DIRS = "dirs"
    FILES = "files"


@dataclass
class Filter:
    def print(self):
        print("Filter print")


@dataclass
class Extension(Filter):
    name: ClassVar = "extension"
    extensions: str = ""


class FilterWithMode(NamedTuple):
    filter: Filter
    mode: Literal["exclude", "include"] = "include"


@dataclass
class Location:
    path: Path


FILTERS = {
    Extension.name: Extension,
}


@dataclass(kw_only=True)
class Rule:
    name: Union[str, None] = Field(default_factory=rule_name)
    enabled: bool = Field(True)
    targets: RuleTarget = RuleTarget.FILES
    locations: List[Location]
    subfolders: bool = False
    tags: List[str] = Field(default_factory=list)
    filters: List[Union[Filter, FilterWithMode]] = Field(default_factory=list)
    filter_mode: FilterMode = FilterMode.ALL
    # actions: List[Action] = Field(..., min_items=1)

    @field_validator("filters", mode="before")
    def validate_filters(cls, value):
        result = []
        for x in value:
            if isinstance(x, str):
                x = {x: None}
            if isinstance(x, dict):
                if not len(x.keys()) == 1:
                    raise ValueError("Filter definition must have a single key")
                name = list(x.keys())[0]
                value = x[name]
                if name.startswith("not "):
                    name = name[4:]
                    mode = "exclude"
                else:
                    mode = "include"
                try:
                    FilterCls = FILTERS[name]
                except KeyError as e:
                    raise ValueError(f'Unknown filter: "{name}"') from e
                if value is None:
                    inst = FilterCls()
                elif isinstance(value, dict):
                    inst = FilterCls(**value)
                else:
                    inst = FilterCls(value)
                result.append(FilterWithMode(filter=inst, mode=mode))

            else:
                result.append(value)
        return result


@dataclass(config=ConfigDict(extra="forbid"))
class Config:
    rules: List[Rule]


config = {
    "rules": [
        {
            "enabled": True,
            "locations": [
                {
                    "path": "~/Test",
                }
            ],
            "filters": [
                "extension",
                {
                    "not extension": ".pdf",
                },
                {
                    "extension": {
                        "extensions": ".txt",
                    },
                },
            ],
        }
    ]
}

conf = Config(**config)
print(conf)

conf2 = Config(
    rules=[
        Rule(
            locations=[],
            filters=[
                Extension(".pdf"),
            ],
        ),
    ]
)
print(conf2)
