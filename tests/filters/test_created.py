from datetime import datetime, timedelta

from arrow import now as arrow_now

from organize.filters import Created
from organize.filters.created import read_created


def test_min():
    now = arrow_now()
    ct = Created(days=10, hours=12, mode="older")
    assert not ct.matches_datetime(now - timedelta(days=10, hours=0))
    assert ct.matches_datetime(now - timedelta(days=10, hours=13))


def test_max():
    now = arrow_now()
    ct = Created(days=10, hours=12, mode="newer")
    assert ct.matches_datetime(now - timedelta(days=10, hours=0))
    assert not ct.matches_datetime(now - timedelta(days=10, hours=13))


def test_read_created(tmp_path):
    f = tmp_path / "file.txt"
    f.touch()
    assert read_created(f).date() == datetime.utcnow().date()
