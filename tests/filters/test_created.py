from datetime import datetime, timedelta

from mock import patch

from organize.compat import Path
from organize.filters import Created
from organize.utils import DotDict


def test_min():
    now = datetime.now()
    created = Created(days=10, hours=12, mode="older")
    with patch.object(created, "_created") as mock_cr:
        mock_cr.return_value = now - timedelta(days=10, hours=0)
        assert created.run(DotDict(path=Path("~"))) is None
        mock_cr.return_value = now - timedelta(days=10, hours=13)
        assert created.run(DotDict(path=Path("~")))


def test_max():
    now = datetime.now()
    created = Created(days=10, hours=12, mode="newer")
    with patch.object(created, "_created") as mock_cr:
        mock_cr.return_value = now - timedelta(days=10, hours=0)
        assert created.run(DotDict(path=Path("~")))
        mock_cr.return_value = now - timedelta(days=10, hours=13)
        assert created.run(DotDict(path=Path("~"))) is None
