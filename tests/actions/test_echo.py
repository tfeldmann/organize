from collections import Counter
from datetime import datetime

from conftest import make_files

from organize import Config


def test_echo_basic(testoutput):
    Config.from_string(
        """
        rules:
          - actions:
              - echo: "Hello World"
        """
    ).execute(simulate=False, output=testoutput)
    assert testoutput.messages == ["Hello World"]


def test_echo_args(testoutput):
    Config.from_string(
        """
        rules:
          - actions:
              - echo: "Date formatting: {now().strftime('%Y')}"
        """
    ).execute(simulate=False, output=testoutput)
    assert testoutput.messages == [f"Date formatting: {datetime.now().year}"]


def test_echo_path(fs, testoutput):
    make_files(["fileA.txt", "fileB.txt"], "test")
    Config.from_string(
        """
        rules:
          - locations: /test
            actions:
              - echo: "{path.stem}"
        """
    ).execute(simulate=False, output=testoutput)
    assert Counter(testoutput.messages) == Counter(["fileA", "fileB"])
