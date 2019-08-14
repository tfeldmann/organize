from organize.filters import Python
from organize.compat import Path
from organize.utils import DotDict


def test_basic():
    p = Python(
        """
        print(attrs.path)
        return 1
        """
    )
    assert p.run(DotDict(path=Path.home()))
    assert p.run(DotDict(path=Path.home())) == {"python": 1}
