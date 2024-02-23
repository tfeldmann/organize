import pytest
from conftest import make_files

from organize import Config


@pytest.mark.parametrize(
    "filter_mode, expected_msgs",
    (
        ("any", ["foo", "x"]),
        ("all", ["foo"]),
        ("none", ["baz"]),
    ),
)
def test_filter_mode(fs, testoutput, filter_mode, expected_msgs):
    make_files(["foo.txt", "baz.bar", "x.txt"], "test")
    config = f"""
    rules:
      - locations: /test
        filters:
          - name: foo
          - extension: txt
        filter_mode: {filter_mode}
        actions:
          - echo: "{{name}}"
    """
    Config.from_string(config).execute(simulate=False, output=testoutput)
    assert testoutput.messages == expected_msgs


@pytest.mark.parametrize(
    "filter_mode, expected_msgs",
    (
        ("any", ["baz", "foo", "x"]),
        ("all", ["x"]),
        ("none", []),
    ),
)
def test_filter_mode_not(fs, testoutput, filter_mode, expected_msgs):
    make_files(["foo.txt", "baz.bar", "x.txt"], "test")
    config = f"""
    rules:
      - locations: /test
        filters:
          - not name: foo
          - extension: txt
        filter_mode: {filter_mode}
        actions:
          - echo: "{{name}}"
    """
    Config.from_string(config).execute(simulate=False, output=testoutput)
    assert testoutput.messages == expected_msgs
