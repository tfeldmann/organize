from datetime import datetime, timedelta

from organize.filters import Created


def test_min():
    now = datetime.now()
    ct = Created(days=10, hours=12, mode="older")
    assert not ct.matches_datetime(now - timedelta(days=10, hours=0))
    assert ct.matches_datetime(now - timedelta(days=10, hours=13))


def test_max():
    now = datetime.now()
    ct = Created(days=10, hours=12, mode="newer")
    assert ct.matches_datetime(now - timedelta(days=10, hours=0))
    assert not ct.matches_datetime(now - timedelta(days=10, hours=13))
