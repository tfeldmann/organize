from pathlib import Path
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
