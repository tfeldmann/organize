from pathlib import Path

from conftest import make_files

from organize import Config


def test_standalone(testoutput):
    Config.from_string(
        """
        rules:
        - actions:
            - echo: "Do this"
            - echo: "And this"
        - actions:
            - echo: "And that"
        """
    ).execute(simulate=False, output=testoutput)
    assert testoutput.messages == ["Do this", "And this", "And that"]
    assert testoutput.msg_report.success_count == 2
    assert testoutput.msg_report.error_count == 0


def test_single_file(fs, testoutput):
    make_files(["foo.txt", "bar.txt"], "/test")
    Config.from_string(
        """
        rules:
          - locations:
              - /test/foo.txt
              - /test/bar.txt
            actions:
              - echo: '{path.name}'
        """
    ).execute(simulate=False, output=testoutput)
    assert testoutput.messages == ["foo.txt", "bar.txt"]


def test_multiple_pathes(fs, testoutput):
    make_files(["foo.txt", "bar.txt"], "/test")
    make_files(["foo.txt", "bar.txt"], "/test2")
    Config.from_string(
        """
        rules:
          - locations:
              - /test
              - /test2
            actions:
              - echo: '{path.name}'
        """
    ).execute(simulate=False, output=testoutput)
    assert testoutput.messages == ["foo.txt", "bar.txt"] * 2


def test_multiple_pathes_single_location(fs, testoutput):
    make_files(["foo.txt", "bar.txt"], "/test")
    make_files(["foo.txt", "bar.txt"], "/test2")
    Config.from_string(
        """
        rules:
          - locations:
              - path:
                - /test
                - /test2
            actions:
              - echo: '{path.name}'
        """
    ).execute(simulate=False, output=testoutput)
    assert testoutput.messages == ["foo.txt", "bar.txt"] * 2


def test_multiple_dirs(fs, testoutput):
    make_files(["foo.txt", "bar.txt"], "/test")
    make_files(["foo.txt", "bar.txt"], "/test2")
    Config.from_string(
        """
        rules:
          - locations:
              - path:
                - /test
                - /test2
            targets: dirs
            actions:
              - echo: '{path.name}'
        """
    ).execute(simulate=False, output=testoutput)
    assert testoutput.messages == []


def test_at_sign_in_path(fs):
    # https://github.com/tfeldmann/organize/issues/332

    test_path = "/CloudStorage/ProtonDrive-xxxx@xxxx.xx/Documents.copy/"

    make_files(["foo.txt", "bar.txt"], "test")
    Config.from_string(
        f"""
        rules:
          - locations: test
            actions:
              - copy: '{test_path}'
        """
    ).execute(simulate=False)

    assert (Path(test_path) / "foo.txt").exists()
    assert (Path(test_path) / "bar.txt").exists()
