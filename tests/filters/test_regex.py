from pathlib import Path

import pytest
from conftest import make_files
from pyfakefs.fake_filesystem import FakeFilesystem

from organize import Config
from organize.filters import Regex
from organize.output import Default
from organize.resource import Resource


def test_regex_backslash():
    regex = Regex(r"^\.pdf$")
    assert regex.matches(".pdf")
    assert not regex.matches("+pdf")
    assert not regex.matches("/pdf")
    assert not regex.matches("\\pdf")


@pytest.mark.parametrize(
    "path,valid,test_result",
    (
        ("RG123456123456-sig.pdf", True, "123456123456"),
        ("RG002312321542-sig.pdf", True, "002312321542"),
        ("RG002312321542.pdf", False, None),
    ),
)
def test_regex_return(path, valid, test_result):
    regex = Regex(r"^RG(?P<the_number>\d{12})-sig\.pdf$")
    assert bool(regex.matches(path)) == valid
    res = Resource(path=Path(path))
    if valid:
        regex.pipeline(res=res, output=Default)
        assert res.vars == {"regex": {"the_number": test_result}}


def test_regex_umlaut():
    regex = Regex(r"^Erträgnisaufstellung-(?P<year>\d*)\.pdf")
    doc = "Erträgnisaufstellung-1998.pdf"
    assert regex.matches(doc)


def test_multiple_regex_placeholders(fs: FakeFilesystem):
    make_files(["test-123.jpg", "other-456.pdf"], "test")

    config = """
    rules:
      - locations: /test/
        filters:
          - regex: (?P<word>\w+)-(?P<number>\d+).*
          - regex: (?P<all>.+?)\.\w{3}
          - extension
        actions:
          - write:
               text: '{regex.word} {regex.number} {regex.all} {extension}'
               outfile: /test/out.txt
    """
    Config.from_string(config).execute(simulate=False)
    out = Path("/test/out.txt").read_text()
    assert "test 123 test-123 jpg" in out
    assert "other 456 other-456 pdf" in out
