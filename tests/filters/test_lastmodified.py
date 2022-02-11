from datetime import datetime, timedelta

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
