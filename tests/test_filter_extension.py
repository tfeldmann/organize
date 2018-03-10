from organize.utils import Path
from organize.filters import Extension


def test_extension():
    extension = Extension('JPG', 'gif', 'pdf')
    testpathes = [
        (Path('~/somefile.pdf'), True),
        (Path('/home/test/somefile.pdf.jpeg'), False),
        (Path('/home/test/gif.TXT'), False),
        (Path('/home/test/txt.GIF'), True),
        (Path('~/somefile.pdf'), True)
    ]
    for path, match in testpathes:
        assert extension.matches(path) == match


def test_extension_empty():
    extension = Extension()
    assert extension.matches(Path('~/test.txt'))


def test_extension_result():
    path = Path('~/somefile.TxT')
    extension = Extension('txt')
    assert extension.matches(path)
    result = extension.parse(path)['extension']
    assert str(result) == '.TxT'
    assert result.lower == '.txt'
    assert result.upper == '.TXT'
