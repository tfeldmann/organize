import fs
from conftest import make_files, read_files

from organize.core import run


def test_rename_issue51(testfs):
    # test for issue https://github.com/tfeldmann/organize/issues/51
    files = {
        "19asd_WF_test2.PDF": "",
        "other.pdf": "",
        "18asd_WFX_test2.pdf": "",
    }
    make_files(testfs, files)

    CONFIG = """
    rules:
      - locations: "./"
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
    run(CONFIG, simulate=False, working_dir=testfs)
    result = read_files(testfs)
    assert result == {
        "copy": {
            "19asd_WF_test2_unread.pdf": "",
        },
        "19asd_WF_test2_unread.pdf": "",
        "other.pdf": "",
        "18asd_WFX_test2.pdf": "",
    }


def test_rename_folders():
    config = """
rules:
  - name: "Renaming DVD folders"
    locations: "/"
    targets: dirs
    filters:
      - name:
          contains: DVD
    actions:
      - rename:
          name: "{name.replace('[DVD] ','').replace(' [1080p]','').replace(' ', '_')}"
"""
    with fs.open_fs("mem://") as mem:
        dir_a = mem.makedir("[DVD] Best Of Video 1080 [1080p]")
        dir_a.touch("[DVD] Best Of Video 1080 [1080p]")
        dir_a.touch("Metadata")
        dir_b = mem.makedir("[DVD] This Is A Title [1080p]")
        dir_b.touch("[DVD] This Is A Title [1080p]")
        dir_b.touch("Metadata")
        run(rules=config, simulate=False, working_dir=mem)
        assert mem.exists("Best_Of_Video_1080")
        assert mem.getinfo("Best_Of_Video_1080").is_dir
        assert mem.exists("This_Is_A_Title")
        assert mem.getinfo("This_Is_A_Title").is_dir
