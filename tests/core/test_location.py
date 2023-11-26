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
