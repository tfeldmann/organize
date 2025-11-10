from conftest import make_files, read_files

from organize import Config
from organize.filters import filecontent


def test_filecontent(fs, monkeypatch):
    # Mock extractor functions for PDF and DOCX - return fixed values
    monkeypatch.setitem(filecontent.SPECIALIZED_EXTRACTORS, ".pdf", lambda _: "PDF")
    monkeypatch.setitem(filecontent.SPECIALIZED_EXTRACTORS, ".docx", lambda _: "DOCX")

    # inspired by https://github.com/tfeldmann/organize/issues/43
    files = {
        "Test1": "Lorem MegaCorp Ltd. ipsum\nInvoice 12345\nMore text\nID: 98765",
        "Test2.txt": "Tests",
        "Test3.txt": "My Homework ...",
        "test4.xml": "XML",
        # Content is not important as we mock extractors
        "test5.pdf": "",
        "test6.docx": "",
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
        - locations: "/test"
          filters:
            - filecontent: '(?P<all>XML|PDF|DOCX)'
          actions:
            - rename: '{filecontent.all}'
        """
    ).execute(simulate=False)
    assert read_files("test") == {
        "Homework.txt": "My Homework ...",
        "MegaCorp_Invoice_12345.txt": "Lorem MegaCorp Ltd. ipsum\nInvoice 12345\nMore text\nID: 98765",
        "Test2.txt": "Tests",
        "XML": "XML",
        "PDF": "",
        "DOCX": "",
    }
