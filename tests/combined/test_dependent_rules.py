from conftest import make_files, read_files

from organize import Config


def test_dependent_rules(fs):
    files = {
        "asd.txt": "",
        "newname 2.pdf": "",
        "newname.pdf": "",
        "test.pdf": "",
    }
    make_files(files, "test")
    Config.from_string(
        """
    rules:
    - locations: "."
      filters:
        - name: test
      actions:
        - copy: newfolder/test.pdf
    - locations: "newfolder"
      filters:
        - name: test
      actions:
        - rename: test-found.pdf
    """
    ).execute(simulate=False)
    assert read_files("test") == {
        "newname.pdf": "",
        "newname 2.pdf": "",
        "test.pdf": "",
        "asd.txt": "",
        "newfolder": {"test-found.pdf": ""},
    }
