from unittest.mock import patch

import pendulum

from pathlib import Path
from organize.filters import LastModified


def test_min():
    now = pendulum.now()
    last_modified = LastModified(days=10, hours=12, mode="older")
    with patch.object(last_modified, "_last_modified") as mock_lm:
        mock_lm.return_value = now - pendulum.duration(days=10, hours=0)
        assert not last_modified.run(path=Path("~"))
        mock_lm.return_value = now - pendulum.duration(days=10, hours=13)
        assert last_modified.run(path=Path("~"))


def test_max():
    now = pendulum.now()
    last_modified = LastModified(days=10, hours=12, mode="newer")
    with patch.object(last_modified, "_last_modified") as mock_lm:
        mock_lm.return_value = now - pendulum.duration(days=10, hours=0)
        assert last_modified.run(path=Path("~"))
        mock_lm.return_value = now - pendulum.duration(days=10, hours=13)
        assert not last_modified.run(path=Path("~"))
