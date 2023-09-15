from enum import Enum
from itertools import count
from pathlib import Path
from typing import Dict, List, Union

from pydantic import BaseModel, Field, field_validator
from pydantic.dataclasses import dataclass
from rich import print

from organize.action import Action
from organize.filter import Filter, Not
from organize.registry import get_action, get_filter, register_action, register_filter

rule_count = count(start=1)


def rule_name():
    global rule_count
    return f"Unnamed rule {next(rule_count)}"


class FilterMode(Enum):
    ALL = "all"
    ANY = "any"
    NONE = "none"


class RuleTarget(Enum):
    DIRS = "dirs"
    FILES = "files"


@dataclass
class Echo:
    msg: str = ""

    def pipeline(res: dict) -> dict:
        print(res)


@dataclass
class Extension:
    extensions: str = ""

    def match(self, res: dict) -> bool:
        return True

    def pipeline(self, res: dict) -> dict:
        return res

    class Meta:
        name: str = "extension"
        supported_targets = ("dirs", "files", "none")


register_filter(Extension, "extension")
register_action(Echo, "echo")


@dataclass
class Location:
    path: Path


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


class Rule(BaseModel, arbitrary_types_allowed=True):
    name: Union[str, None] = Field(default_factory=rule_name)
    enabled: bool = True
    targets: RuleTarget = RuleTarget.FILES
    locations: List[Location] = Field(default_factory=list)
    subfolders: bool = False
    tags: List[str] = Field(default_factory=list)
    filters: List[Filter] = Field(default_factory=list)
    filter_mode: FilterMode = FilterMode.ALL
    actions: List[Action] = Field(..., min_items=1)

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


class Config(BaseModel, extra="forbid"):
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
            "actions": ["echo"],
        }
    ]
}

conf = Config.model_validate(config)
print(conf)

conf2 = Config(
    rules=[
        Rule(
            locations=[],
            filters=[
                Extension(".pdf"),
                Not(Extension(".txt")),
            ],
            actions=[Echo("test")],
        ),
    ]
)
print(conf2)
