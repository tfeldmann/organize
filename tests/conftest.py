import pathlib
from typing import Union
from unittest.mock import patch

import fs
import pytest
from fs.base import FS
from fs.path import basename, join

ORGANIZE_DIR = pathlib.Path(__file__).parent.parent


@pytest.fixture
def tempfs():
    with fs.open_fs("temp://") as tmp:
        yield tmp


@pytest.fixture
def memfs():
    with fs.open_fs("mem://") as mem:
        yield mem


@pytest.fixture(
    params=[
        "mem://",
        pytest.param("temp://"),
    ],
)
def testfs(request) -> FS:
    with fs.open_fs(request.param) as tmp:
        yield tmp


@pytest.fixture
def mock_echo():
    with patch("organize.actions.Echo.print") as mck:
        yield mck


def make_files(fs: FS, layout: Union[dict, list], path="/"):
    """
    Example layout:

        layout = {
            "folder": {
                "subfolder": {
                    "test.txt": "",
                    "other.pdf": b"binary",
                },
            },
            "file.txt": "Hello world\nAnother line",
        }
    """
    fs.makedirs(path, recreate=True)
    if isinstance(layout, list):
        for f in layout:
            fs.touch(f)
        return
    for k, v in layout.items():
        respath = join(path, k)

        # folders are dicts
        if isinstance(v, dict):
            make_files(fs=fs, layout=v, path=respath)

        # everything else is a file
        elif v is None:
            fs.touch(respath)
        elif isinstance(v, bytes):
            fs.writebytes(respath, v)
        elif isinstance(v, str):
            fs.writetext(respath, v)
        else:
            raise ValueError("Unknown file data %s" % v)


def read_files(fs: FS, path="/"):
    result = dict()
    for x in fs.walk.files(path, max_depth=0):
        result[basename(x)] = fs.readtext(x)
    for x in fs.walk.dirs(path, max_depth=0):
        result[basename(x)] = read_files(fs, path=join(path, x))
    return result


def Dir(name: str, *content):
    result = {name: dict()}
    for x in content:
        result[name].update(x)
    return result


def File(name: str, content=""):
    return {name: content}
