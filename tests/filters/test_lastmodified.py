import os
from datetime import datetime, timedelta

from arrow import now as arrow_now
from conftest import make_files, read_files

from organize import Config
from organize.filters import LastModified


def test_min():
    now = arrow_now()
    lm = LastModified(days=10, hours=12, mode="older")
    assert not lm.matches_datetime(now - timedelta(days=10, hours=0))
    assert lm.matches_datetime(now - timedelta(days=10, hours=13))


def test_max():
    now = arrow_now()
    lm = LastModified(days=10, hours=12, mode="newer")
    assert lm.matches_datetime(now - timedelta(days=10, hours=0))
    assert not lm.matches_datetime(now - timedelta(days=10, hours=13))


def test_photo_sorting(fs):
    make_files(["photo1", "photo2", "photo3"], "test")
    conf = """
    rules:
      - locations: /test
        subfolders: true
        filters:
         - lastmodified
        actions:
         - move:
            dest: "/pics/{lastmodified.strftime('%Y/%m/%d')}/"
            on_conflict: skip
    """
    d1 = datetime(2000, 1, 12).timestamp()
    d2 = datetime(2020, 1, 1).timestamp()
    os.utime("/test/photo1", times=(d1, d1))
    os.utime("/test/photo2", times=(d2, d2))
    os.utime("/test/photo3", times=(d2, d2))
    Config.from_string(conf).execute(simulate=False)
    assert read_files("/pics") == {
        "2000": {"01": {"12": {"photo1": ""}}},
        "2020": {"01": {"01": {"photo2": "", "photo3": ""}}},
    }
