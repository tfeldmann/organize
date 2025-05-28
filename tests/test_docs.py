import re

import pytest
from conftest import ORGANIZE_DIR

from organize import Config
from organize.registry import ACTIONS, FILTERS

DOCS_DIR = ORGANIZE_DIR / "docs"

RE_CONFIG = re.compile(r"```yaml\n(?P<config>rules:(?:.*?\n)+?)```", re.MULTILINE)


def _list_examples():
    for f in DOCS_DIR.rglob("*.md"):
        text = f.read_text(encoding="utf-8")
        for n, match in enumerate(RE_CONFIG.findall(text)):
            yield (f"{f} #{n}", match)


@pytest.mark.parametrize(
    "location, config",
    _list_examples(),
    ids=[x[0] for x in _list_examples()],
)
def test_examples_are_valid(location, config):
    """
    Tests all snippets in the docs and readme:
    (To exclude, use shorthand `yml`)

    ```yaml
    rules:
    ```
    """
    try:
        Config.from_string(config)
    except EnvironmentError:
        # in case filters are not supported on the test OS
        pass
    except Exception as e:
        print(f"{location}:\n({config})")
        raise e


def test_all_filters_documented():
    filter_docs = (DOCS_DIR / "filters.md").read_text(encoding="utf-8")
    for name in FILTERS.keys():
        assert "## {}".format(name) in filter_docs, (
            f"The {name} filter is not documented!"
        )


def test_all_actions_documented():
    action_docs = (DOCS_DIR / "actions.md").read_text(encoding="utf-8")
    for name in ACTIONS.keys():
        assert "## {}".format(name) in action_docs, (
            f"The {name} action is not documented!"
        )
