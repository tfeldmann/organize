from organize.filters import Python
from organize.utils import Path


def test_basic():
    p = Python(
        """
        print(path)
        return 1
        """
    )
    assert p.run(path=Path.home())
    assert p.run(path=Path.home()) == {"python": 1}
