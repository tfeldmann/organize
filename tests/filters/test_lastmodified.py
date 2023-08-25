from datetime import datetime, timedelta

from conftest import read_files
from fs.base import FS

from organize import core
from organize.filters import LastModified


def test_min():
    now = datetime.now()
    lm = LastModified(days=10, hours=12, mode="older")
    assert not lm.matches_datetime(now - timedelta(days=10, hours=0))
    assert lm.matches_datetime(now - timedelta(days=10, hours=13))


def test_max():
    now = datetime.now()
    lm = LastModified(days=10, hours=12, mode="newer")
    assert lm.matches_datetime(now - timedelta(days=10, hours=0))
    assert not lm.matches_datetime(now - timedelta(days=10, hours=13))


def test_photo_sorting(testfs: FS):
    conf = """
    rules:
      - locations: "."
        subfolders: true
        filters:
         - lastmodified
        actions:
         - move:
            dest: "./pics/{lastmodified.strftime('%Y/%m/%d')}/"
            on_conflict: skip
    """
    testfs.touch("photo1")
    testfs.touch("photo2")
    testfs.touch("photo3")
    testfs.setinfo(
        "photo1", {"details": {"modified": datetime(2000, 1, 12).timestamp()}}
    )
    testfs.setinfo(
        "photo2", {"details": {"modified": datetime(2020, 1, 1).timestamp()}}
    )
    testfs.setinfo(
        "photo3", {"details": {"modified": datetime(2020, 1, 1).timestamp()}}
    )
    core.run(conf, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {
        "pics": {
            "2000": {"01": {"12": {"photo1": ""}}},
            "2020": {"01": {"01": {"photo2": "", "photo3": ""}}},
        }
    }
