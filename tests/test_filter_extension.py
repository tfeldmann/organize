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
