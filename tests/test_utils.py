from organize.utils import Path, find_unused_filename, splitglob


def test_splitglob():
    assert splitglob('~/Downloads') == (Path.home() / 'Downloads', '')
    assert (
        splitglob('/Test/\* tmp\*/*[!H]/**/*.*') ==
        (Path('/Test/\* tmp\*'), '*[!H]/**/*.*'))
    assert (
        splitglob('~/Downloads/Program 0.1*.exe') ==
        (Path.home() / 'Downloads', 'Program 0.1*.exe'))
    assert (
        splitglob('~/Downloads/Program[ms].exe') ==
        (Path.home() / 'Downloads', 'Program[ms].exe'))
    assert (
        splitglob('~/Downloads/Program.exe') ==
        (Path.home() / 'Downloads' / 'Program.exe', ''))


def test_unused_filename_basic(mock_exists):
    mock_exists.return_value = False
    assert find_unused_filename(Path('somefile.jpg')) == Path('somefile 2.jpg')


def test_unused_filename_multiple(mock_exists):
    mock_exists.side_effect = [True, True, False]
    assert find_unused_filename(Path('somefile.jpg')) == Path('somefile 4.jpg')


def test_unused_filename_increase(mock_exists):
    mock_exists.side_effect = [True, False]
    assert find_unused_filename(
        Path('somefile 7.jpg')) == Path('somefile 9.jpg')


def test_unused_filename_increase_digit(mock_exists):
    mock_exists.side_effect = [True, False]
    assert find_unused_filename(
        Path('7.gif')) == Path('7 3.gif')
