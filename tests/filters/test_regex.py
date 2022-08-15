from pathlib import Path

from organize import core
from organize.filters import Regex

TESTDATA = [
    ("RG123456123456-sig.pdf", True, "123456123456"),
    ("RG002312321542-sig.pdf", True, "002312321542"),
    ("RG002312321542.pdf", False, None),
]


def test_regex_backslash():
    regex = Regex(r"^\.pdf$")
    assert regex.matches(".pdf")
    assert not regex.matches("+pdf")
    assert not regex.matches("/pdf")
    assert not regex.matches("\\pdf")


def test_regex_basic():
    regex = Regex(r"^RG(\d{12})-sig\.pdf$")
    for path, match, _ in TESTDATA:
        assert bool(regex.matches(path)) == match


def test_regex_return():
    regex = Regex(r"^RG(?P<the_number>\d{12})-sig\.pdf$")
    for path, valid, test_result in TESTDATA:
        if valid:
            result = regex.run(fs_path=path)
            assert result.updates == {"regex": {"the_number": test_result}}
            assert result.matches == True


def test_regex_umlaut():
    regex = Regex(r"^Erträgnisaufstellung-(?P<year>\d*)\.pdf")
    doc = "Erträgnisaufstellung-1998.pdf"
    assert regex.matches(doc)
    result = regex.run(fs_path=doc)
    assert result.updates == {"regex": {"year": "1998"}}
    assert result.matches


def test_multiple_regex_placeholders(tempfs):
    config = """
    rules:
      - locations: "."
        filters:
          - regex: (?P<word>\w+)-(?P<number>\d+).*
          - regex: (?P<all>.+?)\.\w{3}
          - extension
        actions:
          - write_text:
               text: '{regex.word} {regex.number} {regex.all} {extension}'
               textfile: out.txt
    """
    tempfs.touch("test-123.jpg")
    tempfs.touch("other-456.pdf")
    core.run(config, simulate=False, working_dir=tempfs)
    out = tempfs.readtext("out.txt")
    assert "test 123 test-123 jpg" in out
    assert "other 456 other-456 pdf" in out
