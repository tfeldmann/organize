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


def test_issue_200(fs):
    # https://github.com/tfeldmann/organize/issues/200
    config = """
    # try to extract the first date from the file and rename it accordingly
    rules:
      - name: date_rename
        locations: scan
        filters:
          - name
          - extension: txt
          - filecontent: '(?P<m>[0123]\d)\.(?P<d>[01]\d)\.(?P<y>[12][09]\d\d)'
        actions:
          - rename: "{filecontent.y}-{filecontent.m}-{filecontent.d}_{name}.txt"
    """
    make_files({"20220401_173738.txt": "Datum: 23.03.2022"}, "scan")
    Config.from_string(config).execute(simulate=False)
    result = read_files("/scan")
    assert result == {
        "2022-23-03_20220401_173738.txt": "Datum: 23.03.2022",
    }
