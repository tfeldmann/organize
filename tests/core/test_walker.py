from collections import Counter
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from organize.walker import Walker


def counter(items):
    return Counter(str(x) for x in items)


def fmt_path(path: str) -> str:
    return f"{Path(path)}"


def test_location(fs):
    fs.create_file("test/folder/file.txt")
    fs.create_file("test/folder/subfolder/another.pdf")
    fs.create_file("test/hi/there")
    fs.create_file("test/hi/.other")
    fs.create_file("test/.hidden/some.pdf")

    assert list(Walker().files("test")) == [
        fmt_path("test/folder/file.txt"),
        fmt_path("test/folder/subfolder/another.pdf"),
        fmt_path("test/hi/there"),
        fmt_path("test/hi/.other"),
        fmt_path("test/.hidden/some.pdf"),
    ]
    assert list(Walker(method="depth").files("test")) == [
        fmt_path("test/folder/subfolder/another.pdf"),
        fmt_path("test/folder/file.txt"),
        fmt_path("test/hi/there"),
        fmt_path("test/hi/.other"),
        fmt_path("test/.hidden/some.pdf"),
    ]


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
            fmt_path("/test/d1/f1.txt"),
            fmt_path("/test/d1/d1/f1.txt"),
            fmt_path("/test/d1/d1/f2.txt"),
            fmt_path("/test/d1/d1/d1/f1.txt"),
            fmt_path("/test/f1.txt"),
        ]
    )

    assert counter(Walker(method=method, min_depth=1).files("/test/")) == counter(
        [
            fmt_path("/test/d1/f1.txt"),
            fmt_path("/test/d1/d1/f1.txt"),
            fmt_path("/test/d1/d1/f2.txt"),
            fmt_path("/test/d1/d1/d1/f1.txt"),
        ]
    )

    assert counter(
        Walker(method=method, min_depth=1, max_depth=2).files("/test/")
    ) == counter(
        [
            fmt_path("/test/d1/f1.txt"),
            fmt_path("/test/d1/d1/f1.txt"),
            fmt_path("/test/d1/d1/f2.txt"),
        ]
    )

    assert counter(
        Walker(method=method, min_depth=2, max_depth=2).files("/test/")
    ) == counter(
        [
            fmt_path("/test/d1/d1/f1.txt"),
            fmt_path("/test/d1/d1/f2.txt"),
        ]
    )

    # dirs
    assert counter(
        Walker(
            method=method,
        ).dirs("/test/")
    ) == counter(
        [
            fmt_path("/test/d1"),
            fmt_path("/test/d1/d1"),
            fmt_path("/test/d1/d1/d1"),
            fmt_path("/test/d1/d2"),
            fmt_path("/test/d1/d3"),
            fmt_path("/test/d1/d1/d2"),
        ]
    )

    assert counter(Walker(method=method, min_depth=1).dirs("/test/")) == counter(
        [
            fmt_path("/test/d1/d1"),
            fmt_path("/test/d1/d1/d1"),
            fmt_path("/test/d1/d2"),
            fmt_path("/test/d1/d3"),
            fmt_path("/test/d1/d1/d2"),
        ]
    )

    assert counter(
        Walker(method=method, min_depth=1, max_depth=2).dirs("/test/")
    ) == counter(
        [
            fmt_path("/test/d1/d1"),
            fmt_path("/test/d1/d1/d1"),
            fmt_path("/test/d1/d2"),
            fmt_path("/test/d1/d3"),
            fmt_path("/test/d1/d1/d2"),
        ]
    )

    assert counter(
        Walker(method=method, min_depth=2, max_depth=2).dirs("/test/")
    ) == counter(
        [
            fmt_path("/test/d1/d1/d1"),
            fmt_path("/test/d1/d1/d2"),
        ]
    )
