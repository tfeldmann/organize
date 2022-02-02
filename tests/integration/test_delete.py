import fs
from conftest import make_files, read_files, organize


def test_delete():
    config = """
    rules:
        -   locations: "files"
            subfolders: true
            actions:
            -   delete
        -   locations: "files"
            targets: dirs
            subfolders: true
            actions:
            -   delete
    """
    files = {
        "files": {
            "folder": {
                "subfolder": {
                    "test.txt": "",
                    "other.pdf": b"binary",
                },
                "file.txt": "Hello world\nAnother line",
            },
        }
    }
    with fs.open_fs("mem://") as mem:
        make_files(mem, files)
        organize(mem, config, simulate=False)
        result = read_files(mem)

        assert result == {
            "files": {},
        }
