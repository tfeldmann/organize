"""
Tests all snippets in the docs and readme like this:

```yaml
rules:
```

To exclude, use shorthand `yml`.
"""

import re

import fs
from schema import SchemaError

from organize.actions import ACTIONS
from organize.config import CONFIG_SCHEMA, load_from_string
from organize.filters import FILTERS

RE_CONFIG = re.compile(r"```yaml\n(?P<config>rules:(?:.*?\n)+?)```", re.MULTILINE)


def test_examples_are_valid():
    docdir = fs.open_fs(".")
    for f in docdir.walk.files(filter=["*.md"], max_depth=2):
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
    filter_docs = docdir.readtext("filters.md")
    for name in FILTERS.keys():
        assert (
            "## {}".format(name) in filter_docs
        ), f"The {name} filter is not documented!"


def test_all_actions_documented():
    docdir = fs.open_fs("docs")
    action_docs = docdir.readtext("actions.md")
    for name in ACTIONS.keys():
        assert (
            "## {}".format(name) in action_docs
        ), f"The {name} action is not documented!"
