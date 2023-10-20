from unittest.mock import patch

from organize import Config


def test_trash_mocked(tmp_path):
    testfile = tmp_path / "test.txt"
    testfile.touch()
    with patch("send2trash.send2trash") as mck:
        Config.from_string(
            f"""
            rules:
              - locations: {tmp_path}
                actions:
                  - trash
            """
        ).execute(simulate=False)
        mck.assert_called_once_with(testfile)


def test_trash_folder(tmp_path):
    testfolder = tmp_path / "test"
    testfolder.mkdir()
    (testfolder / "testfile.txt").touch()
    Config.from_string(
        f"""
        rules:
          - locations: {tmp_path}
            targets: dirs
            actions:
            - trash
        """
    ).execute(simulate=False)
    with patch("send2trash.send2trash") as mck:
        mck.assert_called_once_with(testfolder)
