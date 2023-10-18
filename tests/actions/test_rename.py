from conftest import make_files, read_files

from organize import Config


def test_rename_issue51(fs):
    # test for issue https://github.com/tfeldmann/organize/issues/51
    files = {
        "19asd_WF_test2.PDF": "",
        "other.pdf": "",
        "18asd_WFX_test2.pdf": "",
    }
    make_files(files, "test")

    Config.from_string(
        """
        rules:
          - locations: "/test"
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
    ).execute(simulate=False)
    assert read_files("test") == {
        "copy": {
            "19asd_WF_test2_unread.pdf": "",
        },
        "19asd_WF_test2_unread.pdf": "",
        "other.pdf": "",
        "18asd_WFX_test2.pdf": "",
    }


def test_rename_folders(fs):
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
    make_files(files, "test")
    Config.from_string(
        """
        rules:
          - name: "Renaming DVD folders"
            locations: "/test"
            targets: dirs
            filters:
            - name:
                contains: DVD
            actions:
            - rename:
                new_name: "{name.replace('[DVD] ','').replace(' [1080p]','').replace(' ', '_')}"
        """
    ).execute(simulate=False)
    assert read_files("test") == {
        "Best_Of_Video_1080": {
            "[DVD] Best Of Video 1080 [1080p]": "",
            "Metadata": "",
        },
        "This_Is_A_Title": {
            "[DVD] This Is A Title [1080p]": "",
            "Metadata": "",
        },
    }


def test_rename_in_subfolders(fs):
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
    make_files(files, "test")
    Config.from_string(
        """
        rules:
          - locations: "/test"
            subfolders: true
            filters:
            - name:
                contains: RENAME
            - extension
            actions:
            - rename: "DONE.{extension}"
        """
    ).execute(simulate=False)
    assert read_files("test") == {
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


def test_filename_move(fs):
    make_files({"test.PY": ""}, "test")
    Config.from_string(
        """
        rules:
          - locations: "/test"
            filters:
            - extension
            actions:
            - rename: '{path.stem}{path.stem}.{extension.lower()}'
    """
    ).execute(simulate=False)
    assert read_files("test") == {"testtest.py": ""}
