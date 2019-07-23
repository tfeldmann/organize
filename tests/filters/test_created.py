from datetime import datetime, timedelta

from mock import patch

from organize.filters import Created
from organize.utils import Path


def test_min():
    now = datetime.now()
    created = Created(days=10, hours=12, mode="older")
    with patch.object(created, "_created") as mock_cr:
        mock_cr.return_value = now - timedelta(days=10, hours=0)
        assert not created.matches(Path("~"))
        mock_cr.return_value = now - timedelta(days=10, hours=13)
        assert created.matches(Path("~"))


def test_max():
    now = datetime.now()
    created = Created(days=10, hours=12, mode="newer")
    with patch.object(created, "_created") as mock_cr:
        mock_cr.return_value = now - timedelta(days=10, hours=0)
        assert created.matches(Path("~"))
        mock_cr.return_value = now - timedelta(days=10, hours=13)
        assert not created.matches(Path("~"))
