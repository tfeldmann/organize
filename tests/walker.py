import pytest
import os
from pathlib import Path
from organize.fs import Walker
from pyfakefs.fake_filesystem import FakeFilesystem
from collections import Counter


def counter(items):
    return Counter(str(x) for x in items)


@pytest.mark.skip()
def test_simple(fs):
    for x in os.scandir("."):
        assert "var" not in x.name


def test_breadth(fs: FakeFilesystem):
    fs.create_file("./d1/f1.txt")
    fs.create_file("./d1/d1/f1.txt")
    fs.create_file("./d1/d1/f2.txt")
    fs.create_file("./d1/d1/d1/f1.txt")
    fs.create_file("./f1.txt")
    fs.create_dir("./d1/d2")
    fs.create_dir("./d1/d3")
    fs.create_dir("./d1/d1/d2")

    assert counter(Walker().files(".")) == counter(
        [
            "./d1/f1.txt",
            "./d1/d1/f1.txt",
            "./d1/d1/f2.txt",
            "./d1/d1/d1/f1.txt",
            "./f1.txt",
        ]
    )

    assert counter(Walker(min_depth=1).files("./")) == counter(
        [
            "./d1/f1.txt",
            "./d1/d1/f1.txt",
            "./d1/d1/f2.txt",
            "./d1/d1/d1/f1.txt",
        ]
    )

    assert counter(Walker(min_depth=1, max_depth=2).files("./")) == counter(
        [
            "./d1/f1.txt",
            "./d1/d1/f1.txt",
            "./d1/d1/f2.txt",
        ]
    )

    assert counter(Walker(min_depth=2, max_depth=2).files("./")) == counter(
        [
            "./d1/d1/f1.txt",
            "./d1/d1/f2.txt",
        ]
    )

    # dirs
    assert counter(Walker(exclude_dirs=["var"]).dirs("./")) == counter(
        [
            "./d1",
            "./d1/d1",
            "./d1/d1/d1",
            "./d1/d2",
            "./d1/d3",
            "./d1/d1/d2",
        ]
    )

    assert counter(Walker(exclude_dirs=["var"], min_depth=1).dirs("./")) == counter(
        [
            "./d1/d1",
            "./d1/d1/d1",
            "./d1/d2",
            "./d1/d3",
            "./d1/d1/d2",
        ]
    )

    assert counter(
        Walker(exclude_dirs=["var"], min_depth=1, max_depth=2).dirs("./")
    ) == counter(
        [
            "./d1/d1",
            "./d1/d1/d1",
            "./d1/d2",
            "./d1/d3",
            "./d1/d1/d2",
        ]
    )

    assert counter(
        Walker(exclude_dirs=["var"], min_depth=2, max_depth=2).dirs("./")
    ) == counter(
        [
            "./d1/d1/d1",
            "./d1/d1/d2",
        ]
    )
