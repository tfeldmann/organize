import locale
import subprocess
import sys
from pathlib import Path

from conftest import make_files, read_files

from organize import Config
from organize.filters import filecontent


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


def test_pdftotext_output_does_not_depend_on_locale(monkeypatch):
    # pdftotext writes UTF-8, so its output must not be decoded with the locale
    # encoding (e.g. cp1252 or cp932 on Windows). See issue #492.
    text = "\u6587\u5b57\u5217 Rechnung \u00fcber"
    script = f"import sys; sys.stdout.buffer.write({text.encode('utf-8')!r})"
    real_check_output = subprocess.check_output

    def fake_pdftotext(args, **kwargs):
        assert args[0] == "pdftotext"
        return real_check_output([sys.executable, "-c", script], **kwargs)

    monkeypatch.setattr(locale, "getpreferredencoding", lambda *args: "cp1252")
    monkeypatch.setattr(locale, "getencoding", lambda: "cp1252", raising=False)
    monkeypatch.setattr(filecontent.subprocess, "check_output", fake_pdftotext)

    result = filecontent._extract_with_pdftotext(Path("test.pdf"), keep_layout=True)
    assert result == text
