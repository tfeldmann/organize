import textwrap
from collections import defaultdict

import yaml
from schema import And, Literal, Optional, Or, Schema

from organize.actions import ACTIONS
from organize.filters import FILTERS

from .utils import flatten_all_lists_in_dict

CONFIG_SCHEMA = Schema(
    {
        Literal("rules", description="All rules are defined here."): [
            {
                Optional("name", description="The name of the rule."): str,
                Optional("enabled"): bool,
                Optional("subfolders"): bool,
                Optional("filter_mode", description="The filter mode."): Or(
                    "all", "any", "none", error="Invalid filter mode"
                ),
                Optional("tags"): Or(str, [str]),
                Optional(
                    "targets",
                    description="Whether the rule should apply to directories or folders.",
                ): Or("dirs", "files"),
                "locations": Or(
                    str,
                    [
                        Or(
                            str,
                            {
                                "path": And(str, len),
                                Optional("max_depth"): Or(int, None),
                                Optional("search"): Or("depth", "breadth"),
                                Optional("exclude_files"): Or(str, [str]),
                                Optional("exclude_dirs"): Or(str, [str]),
                                Optional("system_exclude_files"): Or(str, [str]),
                                Optional("system_exclude_dirs"): Or(str, [str]),
                                Optional("filter"): Or(str, [str]),
                                Optional("filter_dirs"): Or(str, [str]),
                                Optional("ignore_errors"): bool,
                                Optional("filesystem"): object,
                            },
                        ),
                    ],
                ),
                Optional("filters"): [
                    Optional(x.get_schema()) for x in FILTERS.values()
                ],
                "actions": [Optional(x.get_schema()) for x in ACTIONS.values()],
            },
        ],
    },
    name="organize rule configuration",
)


def default_yaml_cnst(loader, tag_suffix, node):
    # disable yaml constructors for strings starting with exclamation marks
    # https://stackoverflow.com/a/13281292/300783
    return str(node.tag)


yaml.add_multi_constructor("", default_yaml_cnst, Loader=yaml.SafeLoader)


def load_from_string(config: str) -> dict:
    dedented_config = textwrap.dedent(config)
    return yaml.load(dedented_config, Loader=yaml.SafeLoader)


def lowercase_keys(obj):
    if isinstance(obj, dict):
        obj = {key.lower(): value for key, value in obj.items()}
        for key, value in obj.items():
            if isinstance(value, list):
                for i, item in enumerate(value):
                    value[i] = lowercase_keys(item)
            obj[key] = lowercase_keys(value)
    return obj


def cleanup(config: dict) -> dict:
    result = defaultdict(list)

    # delete every root key except "rules"
    for rule in config.get("rules", []):
        # delete disabled rules
        if rule.get("enabled", True):
            result["rules"].append(rule)

    if not result:
        raise ValueError("No rules defined.")

    result = lowercase_keys(result)

    # flatten all lists everywhere
    return flatten_all_lists_in_dict(dict(result))


def validate(config: dict):
    return CONFIG_SCHEMA.validate(config)
