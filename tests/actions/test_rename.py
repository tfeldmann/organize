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


def test_rename_folders(testfs):
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
    files = {
        "[DVD] Best Of Video 1080 [1080p]": {
            "[DVD] Best Of Video 1080 [1080p]": "",
            "Metadata": "",
        },
        "[DVD] This Is A Title [1080p]": {
            "[DVD] This Is A Title [1080p]": "",
            "Metadata": "",
        },
    }
    make_files(testfs, files)
    run(rules=config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {
        "Best_Of_Video_1080": {
            "[DVD] Best Of Video 1080 [1080p]": "",
            "Metadata": "",
        },
        "This_Is_A_Title": {
            "[DVD] This Is A Title [1080p]": "",
            "Metadata": "",
        },
    }


def test_rename_in_subfolders(testfs):
    config = """
    rules:
      - locations: "/"
        subfolders: true
        filters:
          - name:
              contains: RENAME
          - extension
        actions:
          - rename: "DONE.{extension}"
    """
    files = {
        "folder": {
            "FIRST-RENAME.pdf": "",
            "Other": "",
        },
        "Another folder": {
            "Subfolder": {
                "RENAME-ME_TOO.txt": "",
            },
            "Metadata": "",
        },
    }
    make_files(testfs, files)
    run(rules=config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {
        "folder": {
            "DONE.pdf": "",
            "Other": "",
        },
        "Another folder": {
            "Subfolder": {
                "DONE.txt": "",
            },
            "Metadata": "",
        },
    }
