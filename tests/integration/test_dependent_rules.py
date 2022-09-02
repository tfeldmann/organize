from conftest import make_files, read_files

from organize import core


def test_dependent_rules(testfs):
    files = {
        "asd.txt": "",
        "newname 2.pdf": "",
        "newname.pdf": "",
        "test.pdf": "",
    }
    make_files(testfs, files)
    config = """
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
    core.run(config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {
        "newname.pdf": "",
        "newname 2.pdf": "",
        "test.pdf": "",
        "asd.txt": "",
        "newfolder": {"test-found.pdf": ""},
    }
