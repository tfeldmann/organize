import re

from conftest import ORGANIZE_DIR
from pydantic import ValidationError

from organize import Config
from organize.registry import ACTIONS, FILTERS

DOCS_DIR = ORGANIZE_DIR / "docs"

RE_CONFIG = re.compile(r"```yaml\n(?P<config>rules:(?:.*?\n)+?)```", re.MULTILINE)


def test_examples_are_valid():
    """
    Tests all snippets in the docs and readme:
    (To exclude, use shorthand `yml`)

    ```yaml
    rules:
    ```
    """
    for f in DOCS_DIR.rglob("*.md"):
        text = f.read_text()
        for match in RE_CONFIG.findall(text):
            try:
                Config.from_string(match)
            except ValidationError as e:
                print(f"{f}:\n({match})")
                assert False, "Invalid example config"


def test_all_filters_documented():
    filter_docs = (DOCS_DIR / "filters.md").read_text()
    for name in FILTERS.keys():
        assert (
            "## {}".format(name) in filter_docs
        ), f"The {name} filter is not documented!"


def test_all_actions_documented():
    action_docs = (DOCS_DIR / "actions.md").read_text()
    for name in ACTIONS.keys():
        assert (
            "## {}".format(name) in action_docs
        ), f"The {name} action is not documented!"
