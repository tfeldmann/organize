import fs
from conftest import make_files, read_files

from organize import core


def test_move_on_itself():
    files = {
        "files": {
            "test.txt": "",
            "file.txt": "Hello world\nAnother line",
            "another.txt": "",
            "folder": {
                "x.txt": "",
            },
        }
    }
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

        assert result == {
            "files": {
                "test.txt": "",
                "file.txt": "Hello world\nAnother line",
                "another.txt": "",
                "folder": {
                    "x.txt": "",
                },
            }
        }
