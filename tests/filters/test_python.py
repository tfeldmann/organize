from organize.filters import Python
from organize.utils import Path


def test_basic():
    p = Python(
        """
        print(path)
        return 1
    """
    )
    assert p.matches(path=Path.home())
    assert p.parse(path=Path.home()) == {"python": 1}
