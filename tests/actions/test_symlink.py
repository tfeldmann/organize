from pathlib import Path

from conftest import make_files

from organize import Config


def test_symlink(fs):
    make_files({"file.txt": "Content"}, "test")
    Config.from_string(
        """
        rules:
          - locations: /test
            actions:
              - symlink: /other/
        """
    ).execute(simulate=False)
    target = Path("/other/file.txt")
    assert target.is_symlink()
    assert target.read_text() == "Content"


def test_symlink_dir(fs):
    make_files({"dir": {"file.txt": "Content"}}, "test")
    Config.from_string(
        """
        rules:
          - locations: /test
            targets: dirs
            actions:
              - symlink: /other/
        """
    ).execute(simulate=False)
    target = Path("/other/dir")
    assert target.is_symlink()
    assert (target / "file.txt").read_text() == "Content"
