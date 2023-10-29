from collections import Counter
from datetime import datetime

from conftest import make_files

from organize import Config


def test_echo_basic(msg_output):
    Config.from_string(
        """
        rules:
          - actions:
              - echo: "Hello World"
        """
    ).execute(simulate=False, output=msg_output)
    assert msg_output.messages == ["Hello World"]


def test_echo_args(msg_output):
    Config.from_string(
        """
        rules:
          - actions:
              - echo: "Date formatting: {now().strftime('%Y')}"
        """
    ).execute(simulate=False, output=msg_output)
    assert msg_output.messages == [f"Date formatting: {datetime.now().year}"]


def test_echo_path(fs, msg_output):
    make_files(["fileA.txt", "fileB.txt"], "test")
    Config.from_string(
        """
        rules:
          - locations: /test
            actions:
              - echo: "{path.stem}"
        """
    ).execute(simulate=False, output=msg_output)
    assert Counter(msg_output.messages) == Counter(["fileA", "fileB"])
