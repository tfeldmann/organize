from collections import Counter
from pathlib import Path

import pytest
from conftest import equal_items, make_files
from pyfakefs.fake_filesystem import FakeFilesystem

from organize.walker import Walker


def counter(items):
    return Counter(str(x) for x in items)


def test_location(fs):
    fs.create_file("test/folder/file.txt")
    fs.create_file("test/folder/subfolder/another.pdf")
    fs.create_file("test/hi/there")
    fs.create_file("test/hi/.other")
    fs.create_file("test/.hidden/some.pdf")

    assert equal_items(
        Walker().files("test"),
        [
            Path("test/folder/file.txt"),
            Path("test/folder/subfolder/another.pdf"),
            Path("test/hi/there"),
            Path("test/hi/.other"),
            Path("test/.hidden/some.pdf"),
        ],
    )
    assert equal_items(
        Walker(method="depth").files("test"),
        [
            Path("test/folder/subfolder/another.pdf"),
            Path("test/folder/file.txt"),
            Path("test/hi/there"),
            Path("test/hi/.other"),
            Path("test/.hidden/some.pdf"),
        ],
    )


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

    assert equal_items(
        Walker(method=method).files("/test"),
        [
            Path("/test/d1/f1.txt"),
            Path("/test/d1/d1/f1.txt"),
            Path("/test/d1/d1/f2.txt"),
            Path("/test/d1/d1/d1/f1.txt"),
            Path("/test/f1.txt"),
        ],
    )

    assert equal_items(
        Walker(method=method, min_depth=1).files("/test/"),
        [
            Path("/test/d1/f1.txt"),
            Path("/test/d1/d1/f1.txt"),
            Path("/test/d1/d1/f2.txt"),
            Path("/test/d1/d1/d1/f1.txt"),
        ],
    )

    assert equal_items(
        Walker(method=method, min_depth=1, max_depth=2).files("/test/"),
        [
            Path("/test/d1/f1.txt"),
            Path("/test/d1/d1/f1.txt"),
            Path("/test/d1/d1/f2.txt"),
        ],
    )

    assert equal_items(
        Walker(method=method, min_depth=2, max_depth=2).files("/test/"),
        [
            Path("/test/d1/d1/f1.txt"),
            Path("/test/d1/d1/f2.txt"),
        ],
    )

    # dirs
    assert equal_items(
        Walker(method=method).dirs("/test/"),
        [
            Path("/test/d1"),
            Path("/test/d1/d1"),
            Path("/test/d1/d1/d1"),
            Path("/test/d1/d2"),
            Path("/test/d1/d3"),
            Path("/test/d1/d1/d2"),
        ],
    )

    assert equal_items(
        Walker(method=method, min_depth=1).dirs("/test/"),
        [
            Path("/test/d1/d1"),
            Path("/test/d1/d1/d1"),
            Path("/test/d1/d2"),
            Path("/test/d1/d3"),
            Path("/test/d1/d1/d2"),
        ],
    )

    assert equal_items(
        Walker(method=method, min_depth=1, max_depth=2).dirs("/test/"),
        [
            Path("/test/d1/d1"),
            Path("/test/d1/d1/d1"),
            Path("/test/d1/d2"),
            Path("/test/d1/d3"),
            Path("/test/d1/d1/d2"),
        ],
    )

    assert equal_items(
        Walker(method=method, min_depth=2, max_depth=2).dirs("/test/"),
        [
            Path("/test/d1/d1/d1"),
            Path("/test/d1/d1/d2"),
        ],
    )


def test_exclude_dirs(fs):
    make_files(
        {
            "subA": {"file.a": "", "file.b": ""},
            "subB": {
                "subC": {"file.ca": "", "file.cb": ""},
                "file.ba": "",
                "file.bb": "",
            },
        },
        "test",
    )
    assert len(list(Walker(exclude_dirs=["subC"]).files("/test"))) == 4


def test_order(fs):
    make_files(
        {
            "2024": {"004": "", "001": "", "003": "", "002": ""},
            "1989": {"D": "", "C": "", "A": "", "B": ""},
            "2000": {"B": {"2": "", "1": ""}, "A": {"1": "", "2": ""}},
        },
        "test",
    )
    assert list(Walker().files("/test")) == [
        Path("/test/1989/A"),
        Path("/test/1989/B"),
        Path("/test/1989/C"),
        Path("/test/1989/D"),
        Path("/test/2000/A/1"),
        Path("/test/2000/A/2"),
        Path("/test/2000/B/1"),
        Path("/test/2000/B/2"),
        Path("/test/2024/001"),
        Path("/test/2024/002"),
        Path("/test/2024/003"),
        Path("/test/2024/004"),
    ]
