from conftest import make_files

from organize import Config


def test_relative_path(fs):
    make_files(["test.txt"], "test")
    conf = """
    rules:
      - locations: /test
        actions:
          - move: "/other/path/"
          - echo: "{relative_path}"
    """
    Config.from_string(conf).execute(simulate=False)
