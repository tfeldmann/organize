import pytest
from conftest import make_files, read_files

from organize import Config

FILES = {
    "test.txt": "",
    "file.txt": "Hello world\nAnother line",
    "another.txt": "",
    "folder": {
        "x.txt": "",
    },
}


def test_copy_on_itself(fs):
    make_files(FILES, "test")
    config = """
    rules:
      - locations: "test"
        actions:
          - copy: "test"
    """
    Config.from_string(config).execute(simulate=False)
    result = read_files("test")
    assert result == FILES


def test_copy_basic(fs):
    config = """
    rules:
      - locations: "test"
        filters:
          - name: test
        actions:
          - copy: test/newname.pdf
    """
    make_files(["asd.txt", "newname 2.pdf", "newname.pdf", "test.pdf"], "test")
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {
        "newname.pdf": "",
        "newname 2.pdf": "",
        "newname 3.pdf": "",
        "test.pdf": "",
        "asd.txt": "",
    }


def test_copy_into_dir(fs):
    make_files(FILES, "test")
    config = """
    rules:
      - locations: "test"
        actions:
          - copy: "test/a brand/new/folder/"
    """
    Config.from_string(config).execute(simulate=False)
    result = read_files("test")
    assert result == {
        "test.txt": "",
        "file.txt": "Hello world\nAnother line",
        "another.txt": "",
        "folder": {
            "x.txt": "",
        },
        "a brand": {
            "new": {
                "folder": {
                    "test.txt": "",
                    "file.txt": "Hello world\nAnother line",
                    "another.txt": "",
                }
            }
        },
    }


def test_copy_into_dir_subfolders(fs):
    make_files(FILES, "test")
    config = """
    rules:
      - locations: "/test"
        subfolders: true
        actions:
          - copy: "/test/a brand/new/folder/"
    """
    Config.from_string(config).execute(simulate=False)
    result = read_files("test")
    assert result == {
        "test.txt": "",
        "file.txt": "Hello world\nAnother line",
        "another.txt": "",
        "folder": {
            "x.txt": "",
        },
        "a brand": {
            "new": {
                "folder": {
                    "test.txt": "",
                    "file.txt": "Hello world\nAnother line",
                    "another.txt": "",
                    "x.txt": "",
                }
            }
        },
    }


@pytest.mark.parametrize(
    "mode,result",
    [
        ("skip", {"src.txt": "src", "dst.txt": "dst"}),
        ("overwrite", {"src.txt": "src", "dst.txt": "src"}),
        ("rename_new", {"src.txt": "src", "dst.txt": "dst", "dst 2.txt": "src"}),
        ("rename_existing", {"src.txt": "src", "dst.txt": "src", "dst 2.txt": "dst"}),
    ],
)
def test_copy_conflict(fs, mode, result):
    make_files(
        {
            "src.txt": "src",
            "dst.txt": "dst",
        },
        path="test",
    )
    config = f"""
    rules:
      - locations: "/test"
        filters:
          - name: src
        actions:
          - copy:
              dest: "/test/dst.txt"
              on_conflict: {mode}
    """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == result


def test_copy_deduplicate_conflict(fs):
    files = {
        "src.txt": "src",
        "duplicate": {
            "src.txt": "src",
        },
        "nonduplicate": {
            "src.txt": "src2",
        },
    }

    config = """
    rules:
      - locations: "/test"
        subfolders: true
        filters:
          - name: src
        actions:
          - copy:
              dest: "/test/dst.txt"
              on_conflict: deduplicate
    """
    make_files(files, "test")

    Config.from_string(config).execute(simulate=False)
    result = read_files("test")

    assert result == {
        "src.txt": "src",
        "duplicate": {
            "src.txt": "src",
        },
        "nonduplicate": {
            "src.txt": "src2",
        },
        "dst.txt": "src",
        "dst 2.txt": "src2",
    }


def test_does_not_create_folder_in_simulation(fs):
    config = """
        rules:
          - locations: "/test"
            actions:
              - copy: "/test/new-subfolder/"
              - copy: "/test/copyhere/"
        """
    make_files(FILES, "test")
    Config.from_string(config).execute(simulate=True)
    result = read_files("test")
    assert result == FILES
