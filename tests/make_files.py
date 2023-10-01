from pathlib import Path

from conftest import make_files, read_files


def test_make_files(fs):
    files = {
        "folder": {
            "subfolder": {
                "test.txt": "",
                "other.pdf": "text",
            },
        },
        "file.txt": "Hello world\nAnother line",
    }

    make_files(files, "test")
    assert read_files("test") == files
