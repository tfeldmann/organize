from conftest import make_files, read_files

from organize import Config


def test_is_executable():
    import sys
    from uuid import uuid1 as uuid
    from organize.filters.filecontent import _is_executable as is_executable

    present_exe = "dir" if hasattr(sys, "getwindowsversion") else "ls"
    assert is_executable(present_exe)

    absent_exe = f"no-such-executable-{uuid()}"  # random name that won't exist
    assert not is_executable(absent_exe)


def test_filecontent(fs):
    # inspired by https://github.com/tfeldmann/organize/issues/43
    files = {
        "Test1.txt": "Lorem MegaCorp Ltd. ipsum\nInvoice 12345\nMore text\nID: 98765",
        "Test2.txt": "Tests",
        "Test3.txt": "My Homework ...",
    }
    make_files(files, "test")
    Config.from_string(
        r"""
        rules:
        - locations: "/test"
          filters:
            - filecontent: 'MegaCorp Ltd.+^Invoice (?P<number>\w+)$.+^ID: 98765$'
          actions:
            - rename: "MegaCorp_Invoice_{filecontent.number}.txt"
        - locations: "/test"
          filters:
            - filecontent: '.*Homework.*'
          actions:
            - rename: "Homework.txt"
        """
    ).execute(simulate=False)
    assert read_files("test") == {
        "Homework.txt": "My Homework ...",
        "MegaCorp_Invoice_12345.txt": "Lorem MegaCorp Ltd. ipsum\nInvoice 12345\nMore text\nID: 98765",
        "Test2.txt": "Tests",
    }
