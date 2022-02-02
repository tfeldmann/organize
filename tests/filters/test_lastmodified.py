from datetime import datetime, timedelta

from organize.filters import LastModified


def test_min():
    now = datetime.now()
    lastmodified = LastModified(days=10, hours=12, mode="older")
    assert not lastmodified.matches_lastmodified_time(now - timedelta(days=10, hours=0))
    assert lastmodified.matches_lastmodified_time(now - timedelta(days=10, hours=13))


def test_max():
    now = datetime.now()
    lastmodified = LastModified(days=10, hours=12, mode="newer")
    assert lastmodified.matches_lastmodified_time(now - timedelta(days=10, hours=0))
    assert not lastmodified.matches_lastmodified_time(
        now - timedelta(days=10, hours=13)
    )
