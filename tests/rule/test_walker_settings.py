from unittest.mock import call
from organize.rule import Rule


def test_walker_settings():
    rule = Rule()
    _, conf = rule.walker_settings("~/Documents", {"search": "depth"})
    assert conf["search"] == "depth"

def test_glob():
    rule = Rule()
    folder, conf = rule.walker_settings("~/Documents/*.h", {})
    assert folder == "~/Documents"
    assert conf["filter"] == ["*.h"]
    assert conf["max_depth"] == 0

    folder, conf = rule.walker_settings("~/Documents/**/*.h", {})
    assert folder == "~/Documents"
    assert conf["filter"] == ["*.h"]
    assert conf["max_depth"] is None
