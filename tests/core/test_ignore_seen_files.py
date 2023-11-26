from conftest import make_files, read_files

from organize import Config


def test_ignore_seen_files(fs):
    make_files(
        {
            "sub": {},
            "foo.txt": "",
            "bar.txt": "",
        },
        "test",
    )
    config = """
    rules:
      - locations: /test
        subfolders: true
        actions:
          - move: "{path.parent}/sub/{path.name}"
    """
    Config.from_string(config).execute(simulate=False)
    result = read_files("test")
    assert result == {
        "sub": {
            "foo.txt": "",
            "bar.txt": "",
        }
    }
