from unittest.mock import call
from organize.organizer import Organizer


def test_organizer():
    org = Organizer()
    _, conf = org.walker_settings("~/Documents", {"search": "depth"})
    assert conf["search"] == "depth"

def test_glob():
    org = Organizer()
    folder, conf = org.walker_settings("~/Documents/*.h", {})
    assert folder == "~/Documents"
    assert conf["filter"] == ["*.h"]
    assert conf["max_depth"] == 0

    folder, conf = org.walker_settings("~/Documents/**/*.h", {})
    assert folder == "~/Documents"
    assert conf["filter"] == ["*.h"]
    assert conf["max_depth"] is None
