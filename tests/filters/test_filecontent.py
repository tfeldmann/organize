import pytest
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


def _pdf_with_text(text: str) -> bytes:
    stream = f"BT /F1 24 Tf 72 700 Td ({text}) Tj ET".encode()
    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
        b"/Resources<</Font<</F1 5 0 R>>>>/Contents 4 0 R>>",
        b"<</Length %d>>stream\n" % len(stream) + stream + b"\nendstream",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for nr, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % nr + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer<</Size %d/Root 1 0 R>>\nstartxref\n%d\n%%%%EOF\n" % (
        len(objects) + 1,
        xref,
    )
    return out


def _mime_wrap(data: bytes, base64_encode: bool = False) -> bytes:
    import base64

    boundary = b"------=_Part_1_2.3"
    headers = b"Content-Type: application/pdf; name=Bill\r\n"
    if base64_encode:
        headers += b"Content-Transfer-Encoding: base64\r\n"
        data = base64.encodebytes(data)
    return boundary + b"\r\n" + headers + b"\r\n" + data + b"\r\n" + boundary + b"--"


@pytest.mark.parametrize("base64_encode", [False, True])
def test_mime_wrapped_pdf(tmp_path, base64_encode):
    pdf = _pdf_with_text("Invoice 4711")
    path = tmp_path / "Bill.pdf"
    path.write_bytes(_mime_wrap(pdf, base64_encode=base64_encode))
    assert filecontent.pdf_bytes(path) == pdf
    assert "Invoice 4711" in filecontent.textract(path)


def test_plain_pdf_bytes(tmp_path):
    pdf = _pdf_with_text("Hello")
    path = tmp_path / "plain.pdf"
    path.write_bytes(pdf)
    assert filecontent.pdf_bytes(path) == pdf
    (tmp_path / "html.pdf").write_bytes(b"<html></html>")
    assert filecontent.pdf_bytes(tmp_path / "html.pdf") is None
