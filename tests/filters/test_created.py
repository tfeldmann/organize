from datetime import datetime, timedelta

from organize.filters import Created


def test_min():
    now = datetime.now()
    created = Created(days=10, hours=12, mode="older")
    assert not created.matches_created_time(now - timedelta(days=10, hours=0))
    assert created.matches_created_time(now - timedelta(days=10, hours=13))


def test_max():
    now = datetime.now()
    created = Created(days=10, hours=12, mode="newer")
    assert created.matches_created_time(now - timedelta(days=10, hours=0))
    assert not created.matches_created_time(now - timedelta(days=10, hours=13))
