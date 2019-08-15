from datetime import datetime, timedelta

from mock import patch

from organize.compat import Path
from organize.filters import LastModified


def test_min():
    now = datetime.now()
    last_modified = LastModified(days=10, hours=12, mode="older")
    with patch.object(last_modified, "_last_modified") as mock_lm:
        mock_lm.return_value = now - timedelta(days=10, hours=0)
        assert not last_modified.run(path=Path("~"))
        mock_lm.return_value = now - timedelta(days=10, hours=13)
        assert last_modified.run(path=Path("~"))


def test_max():
    now = datetime.now()
    last_modified = LastModified(days=10, hours=12, mode="newer")
    with patch.object(last_modified, "_last_modified") as mock_lm:
        mock_lm.return_value = now - timedelta(days=10, hours=0)
        assert last_modified.run(path=Path("~"))
        mock_lm.return_value = now - timedelta(days=10, hours=13)
        assert not last_modified.run(path=Path("~"))
