from conftest import make_files, read_files

from organize import Config

FILES = {
    "test.txt": "",
    "file.txt": "Hello world\nAnother line",
    "another.txt": "",
    "folder": {
        "x.txt": "",
        "empty_sub": {},
    },
    "empty_folder": {},
}


def test_delete_empty_files(fs):
    config = """
    rules:
      - name: "Recursively delete all empty files"
        locations:
          - path: "test"
        subfolders: true
        filters:
          - empty
        actions:
          - delete
    """
    make_files(FILES, "test")
    Config.from_string(config).execute(simulate=False)
    result = read_files("test")
    assert result == {
        "file.txt": "Hello world\nAnother line",
        "folder": {
            "empty_sub": {},
        },
        "empty_folder": {},
    }


def test_delete_empty_dirs(fs):
    config = """
    rules:
    - name: "Recursively delete all empty directories"
      locations: "test"
      subfolders: true
      targets: dirs
      filters:
        - empty
      actions:
        - delete
    """
    make_files(FILES, "test")
    Config.from_string(config).execute(simulate=False)
    result = read_files("test")
    assert result == {
        "test.txt": "",
        "file.txt": "Hello world\nAnother line",
        "another.txt": "",
        "folder": {
            "x.txt": "",
        },
    }


def test_delete_deep(fs):
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
    make_files(files, "test")
    config = """
    rules:
      - locations: "test"
        actions:
          - delete
      - locations: "test"
        targets: dirs
        actions:
          - delete
    """
    # sim
    Config.from_string(config).execute(simulate=True)
    result = read_files("test")
    assert result == files

    # run
    Config.from_string(config).execute(simulate=False)
    result = read_files("test")
    assert result == {}
