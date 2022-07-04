from copy import deepcopy

import fs
from conftest import make_files, read_files

from organize import core

files = {
    "files": {
        "test.txt": "",
        "file.txt": "Hello world\nAnother line",
        "another.txt": "",
        "folder": {
            "x.txt": "",
        },
    },
    "min": {},
    "max": {},
}

def test_depth_options():
    with fs.open_fs("mem://") as mem:
        config = {
            "rules": [{
                "locations": [
                    {"path": "files", "filesystem": mem, "min_depth": 1},
                ],
                "actions": [
                    {"copy": {"dest": "min/", "filesystem": mem}},
                ],
                "subfolders": True
            },{
                "locations": [
                    {"path": "files", "filesystem": mem, "max_depth": 1},
                ],
                "actions": [
                    {"copy": {"dest": "max/", "filesystem": mem}},
                ],
                "subfolders": True
            }]
        }
        make_files(mem, files)
        core.run(config, simulate=False)
        result = read_files(mem)
        assert len(result["min"].keys()) == 1
        assert len(result["max"].keys()) == 3


def test_copy_on_itself():
    with fs.open_fs("mem://") as mem:
        config = {
            "rules": [
                {
                    "locations": [
                        {"path": "files", "filesystem": mem},
                    ],
                    "actions": [
                        {"copy": {"dest": "files/", "filesystem": mem}},
                    ],
                },
            ]
        }
        make_files(mem, files)
        core.run(config, simulate=False)
        result = read_files(mem)
        assert result == files


def test_does_not_create_folder_in_simulation():
    with fs.open_fs("mem://") as mem:
        config = {
            "rules": [
                {
                    "locations": [
                        {"path": "files", "filesystem": mem},
                    ],
                    "actions": [
                        {"copy": {"dest": "files/new-subfolder/", "filesystem": mem}},
                        {"copy": {"dest": "files/copyhere/", "filesystem": mem}},
                    ],
                },
            ]
        }
        make_files(mem, files)
        core.run(config, simulate=True)
        result = read_files(mem)
        assert result == files

        core.run(config, simulate=False, validate=False)
        result = read_files(mem)

        expected = deepcopy(files)
        expected["files"]["new-subfolder"] = deepcopy(files["files"])
        expected["files"]["new-subfolder"].pop("folder")
        expected["files"]["copyhere"] = deepcopy(files["files"])
        expected["files"]["copyhere"].pop("folder")

        assert result == expected
