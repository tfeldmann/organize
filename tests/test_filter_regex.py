from organize.utils import Path
from organize.filters import Regex


TESTDATA = [
    (Path('~/Invoices/RG123456123456-sig.pdf'), True, '123456123456'),
    (Path('~/Invoices/RG002312321542-sig.pdf'), True, '002312321542'),
    (Path('~/Invoices/RG002312321542.pdf'), False, None),
]


def test_regex_backslash():
    regex = Regex('^\.pdf$')
    assert regex.matches(Path('.pdf'))
    assert not regex.matches(Path('+pdf'))
    assert not regex.matches(Path('/pdf'))
    assert not regex.matches(Path('\pdf'))


def test_regex_basic():
    regex = Regex('^RG(\d{12})-sig\.pdf$')
    for path, match, _ in TESTDATA:
        assert regex.matches(path) == match


def test_regex_return():
    regex = Regex('^RG(?P<the_number>\d{12})-sig\.pdf$')
    for path, valid, result in TESTDATA:
        if valid:
            attrs = regex.parse(path)
            assert attrs['regex'].the_number == result
