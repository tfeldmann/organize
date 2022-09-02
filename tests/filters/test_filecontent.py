from conftest import make_files, read_files

from organize import core


def test_filecontent(tempfs):
    # inspired by https://github.com/tfeldmann/organize/issues/43
    files = {
        "Test1.txt": "Lorem MegaCorp Ltd. ipsum\nInvoice 12345\nMore text\nID: 98765",
        "Test2.txt": "Tests",
        "Test3.txt": "My Homework ...",
    }
    make_files(tempfs, files)
    config = r"""
        rules:
        - locations: "."
          filters:
            - filecontent: 'MegaCorp Ltd.+^Invoice (?P<number>\w+)$.+^ID: 98765$'
          actions:
            - rename: "MegaCorp_Invoice_{filecontent.number}.txt"
        - locations: "."
          filters:
            - filecontent: '.*Homework.*'
          actions:
            - rename: "Homework.txt"
        """
    core.run(config, simulate=False, working_dir=tempfs)
    assert read_files(tempfs) == {
        "Homework.txt": "My Homework ...",
        "MegaCorp_Invoice_12345.txt": "Lorem MegaCorp Ltd. ipsum\nInvoice 12345\nMore text\nID: 98765",
        "Test2.txt": "Tests",
    }
