import fs
from conftest import make_files, read_files

from organize import core

CONFIG = """
rules:
  - locations: "."
    filters:
      - extension
      - name:
          startswith: "19"
          contains:
            - "_WF_"
    actions:
      - rename: "{name}_unread.{extension.lower()}"
      - copy:
          dest: "copy/"
"""


def test_rename_issue52(testfs):
    # test for issue https://github.com/tfeldmann/organize/issues/51
    files = {
        "19asd_WF_test2.PDF": "",
        "other.pdf": "",
        "18asd_WFX_test2.pdf": "",
    }
    make_files(testfs, files)
    core.run(CONFIG, simulate=False, working_dir=testfs)
    testfs.tree()
    result = read_files(testfs)
    assert result == {
        "copy": {
            "19asd_WF_test2_unread.pdf": "",
        },
        "19asd_WF_test2_unread.pdf": "",
        "other.pdf": "",
        "18asd_WFX_test2.pdf": "",
    }
