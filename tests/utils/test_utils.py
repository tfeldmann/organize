import pytest
from fs.osfs import OSFS
from os.path import expanduser
from organize.utils import fs_path_expand


OSFS_ROOT = OSFS("/")
DESKTOP_WITH_USER = expanduser("~/Desktop")


@pytest.mark.parametrize(
    "fs,path,args,result_fs,result_path",
    [
        (None, "~/Desktop", None, DESKTOP_WITH_USER, "/"),
        (OSFS_ROOT, "/etc", None, OSFS_ROOT, "/etc"),
        ("~/Desktop", "/etc", None, DESKTOP_WITH_USER, "/etc"),
        ("~/Desktop", "/etc/{name}", {"name": "test"}, DESKTOP_WITH_USER, "/etc/test"),
        ("{env.HOME}/Desktop", "/", {"name": "test"}, DESKTOP_WITH_USER, "/"),
    ],
)
def test_fs_path_from_options(fs, path, args, result_fs, result_path):
    assert fs_path_expand(fs=fs, path=path, args=args) == (result_fs, result_path)
