import re

import fs
from schema import SchemaError

from organize.filters import FILTERS
from organize.actions import ACTIONS
from organize.config import CONFIG_SCHEMA, load_from_string

RE_CONFIG = re.compile(r"```yaml\n(?P<config>rules:(?:.*?\n)+?)```", re.MULTILINE)


DOCS = {
    "filters": "03-filters.md",
    "actions": "04-actions.md",
}


def test_examples_are_valid():
    docdir = fs.open_fs("docs")
    for f in DOCS.values():
        text = docdir.readtext(f)
        for match in RE_CONFIG.findall(text):
            err = ""
            try:
                config = load_from_string(match)
                CONFIG_SCHEMA.validate(config)
            except SchemaError as e:
                print(f"{f}:\n({match})")
                err = e.autos[-1]
            assert not err


def test_all_filters_documented():
    docdir = fs.open_fs("docs")
    filter_docs = docdir.readtext(DOCS["filters"])
    for name in FILTERS.keys():
        assert "## {}".format(name) in filter_docs


def test_all_actions_documented():
    docdir = fs.open_fs("docs")
    action_docs = docdir.readtext(DOCS["actions"])
    for name in ACTIONS.keys():
        assert "## {}".format(name) in action_docs
