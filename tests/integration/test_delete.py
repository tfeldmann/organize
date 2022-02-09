import fs
from conftest import make_files, read_files

from organize import core


def test_delete():
    files = {
        "files": {
            "folder": {
                "subfolder": {
                    "test.txt": "",
                    "other.pdf": "binary",
                },
                "file.txt": "Hello world\nAnother line",
            },
        }
    }
    with fs.open_fs("mem://") as mem:
        config = {
            "rules": [
                {
                    "locations": [{"path": "files", "filesystem": mem}],
                    "actions": ["delete"],
                },
                {
                    "locations": [{"path": "files", "filesystem": mem}],
                    "targets": "dirs",
                    "actions": ["delete"],
                },
            ]
        }
        make_files(mem, files)

        # simulate
        core.run(config, simulate=True)
        result = read_files(mem)
        assert result == files

        # run
        core.run(config, simulate=False, validate=False)
        result = read_files(mem)
        assert result == {
            "files": {},
        }
