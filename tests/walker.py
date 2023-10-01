from collections import Counter

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from organize.walker import Walker


def counter(items):
    return Counter(str(x) for x in items)


@pytest.mark.parametrize("method", ("depth", "breadth"))
def test_walk(fs: FakeFilesystem, method):
    fs.create_file("/test/d1/f1.txt")
    fs.create_file("/test/d1/d1/f1.txt")
    fs.create_file("/test/d1/d1/f2.txt")
    fs.create_file("/test/d1/d1/d1/f1.txt")
    fs.create_file("/test/f1.txt")
    fs.create_dir("/test/d1/d2")
    fs.create_dir("/test/d1/d3")
    fs.create_dir("/test/d1/d1/d2")

    assert counter(Walker(method=method).files("/test")) == counter(
        [
            "/test/d1/f1.txt",
            "/test/d1/d1/f1.txt",
            "/test/d1/d1/f2.txt",
            "/test/d1/d1/d1/f1.txt",
            "/test/f1.txt",
        ]
    )

    assert counter(Walker(method=method, min_depth=1).files("/test/")) == counter(
        [
            "/test/d1/f1.txt",
            "/test/d1/d1/f1.txt",
            "/test/d1/d1/f2.txt",
            "/test/d1/d1/d1/f1.txt",
        ]
    )

    assert counter(
        Walker(method=method, min_depth=1, max_depth=2).files("/test/")
    ) == counter(
        [
            "/test/d1/f1.txt",
            "/test/d1/d1/f1.txt",
            "/test/d1/d1/f2.txt",
        ]
    )

    assert counter(
        Walker(method=method, min_depth=2, max_depth=2).files("/test/")
    ) == counter(
        [
            "/test/d1/d1/f1.txt",
            "/test/d1/d1/f2.txt",
        ]
    )

    # dirs
    assert counter(
        Walker(
            method=method,
        ).dirs("/test/")
    ) == counter(
        [
            "/test/d1",
            "/test/d1/d1",
            "/test/d1/d1/d1",
            "/test/d1/d2",
            "/test/d1/d3",
            "/test/d1/d1/d2",
        ]
    )

    assert counter(Walker(method=method, min_depth=1).dirs("/test/")) == counter(
        [
            "/test/d1/d1",
            "/test/d1/d1/d1",
            "/test/d1/d2",
            "/test/d1/d3",
            "/test/d1/d1/d2",
        ]
    )

    assert counter(
        Walker(method=method, min_depth=1, max_depth=2).dirs("/test/")
    ) == counter(
        [
            "/test/d1/d1",
            "/test/d1/d1/d1",
            "/test/d1/d2",
            "/test/d1/d3",
            "/test/d1/d1/d2",
        ]
    )

    assert counter(
        Walker(method=method, min_depth=2, max_depth=2).dirs("/test/")
    ) == counter(
        [
            "/test/d1/d1/d1",
            "/test/d1/d1/d2",
        ]
    )
