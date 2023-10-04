import pytest
from conftest import make_files, read_files

from organize.config import Config


def test_move_onto_itself(fs):
    FILES = {
        "test.txt": "",
        "file.txt": "Hello world\nAnother line",
        "another.txt": "",
        "folder": {
            "x.txt": "",
        },
    }
    make_files(FILES, "test")
    config = """
    rules:
      - locations: "test"
        actions:
          - move: "test"
    """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == FILES


@pytest.mark.parametrize(
    "mode,result",
    [
        ("skip", {"src.txt": "src", "dst.txt": "dst"}),
        ("overwrite", {"dst.txt": "src"}),
        ("rename_new", {"dst 2.txt": "src", "dst.txt": "dst"}),
        ("rename_existing", {"dst.txt": "src", "dst 2.txt": "dst"}),
    ],
)
def test_move_conflict(fs, mode, result):
    make_files(
        {
            "src.txt": "src",
            "dst.txt": "dst",
        },
        path="test",
    )
    # src is moved onto dst.
    config = f"""
    rules:
      - locations: "test"
        filters:
          - name: src
        actions:
          - move:
              dest: "{{location}}/dst.txt"
              on_conflict: {mode}
    """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == result


def test_move_folder_conflict(fs):
    make_files(
        {
            "src": {"dir": {"src.txt": ""}},
            "dst": {"dir": {"dst.txt": ""}},
        },
        "test",
    )
    # src is moved onto dst.
    Config.from_string(
        """
        rules:
            -   locations: "/test/src"
                targets: dirs
                filters:
                    - name: dir
                actions:
                    - move:
                        dest: "{location}/../dst"
                        on_conflict: "rename_new"
        """
    ).execute(simulate=False)
    assert read_files("test") == {
        "src": {},
        "dst": {
            "dir": {"dst.txt": ""},
            "dir 2": {"src.txt": ""},
        },
    }
