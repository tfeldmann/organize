import textwrap

import yaml
from schema import And, Optional, Or, Schema, Literal

from organize.actions import ACTIONS
from organize.filters import FILTERS

CONFIG_SCHEMA = Schema(
    {
        Literal("rules", description="All rules are defined here."): [
            {
                Optional("name", description="The name of the rule."): str,
                Optional("enabled"): bool,
                Optional("subfolders"): bool,
                Optional("filter_mode", description="The filter mode."): Or(
                    "all", "any", "none", error='Invalid filter mode'
                ),
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
                                Optional("exclude_files"): [str],
                                Optional("exclude_dirs"): [str],
                                Optional("system_exlude_files"): [str],
                                Optional("system_exclude_dirs"): [str],
                                Optional("ignore_errors"): bool,
                                Optional("filter"): [str],
                                Optional("filter_dirs"): [str],
                                Optional("filesystem"): str,
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


def load_from_string(config):
    dedented_config = textwrap.dedent(config)
    return yaml.load(dedented_config, Loader=yaml.SafeLoader)


def load_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return load_from_string(f.read())
