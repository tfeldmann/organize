from organize.utils import Path, find_unused_filename, splitglob, increment_filename_version


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


def test_unused_filename_separator(mock_exists):
    mock_exists.return_value = False
    assert find_unused_filename(
        Path('somefile.jpg'), separator='_') == Path('somefile_2.jpg')


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


def test_increment_filename_version():
    assert (
        increment_filename_version(Path.home() / 'f3' / 'test_123.7z') ==
        Path.home() / 'f3' / 'test_123 2.7z')
    assert (
        increment_filename_version(Path.home() / 'f3' / 'test_123_2 10.7z') ==
        Path.home() / 'f3' / 'test_123_2 11.7z')


def test_increment_filename_version_separator():
    assert increment_filename_version(
        Path('test_123.7z'), separator='_') == Path('test_124.7z')
    assert increment_filename_version(
        Path('test_123_2.7z'), separator='_') == Path('test_123_3.7z')


def test_increment_filename_version_no_separator():
    assert increment_filename_version(
        Path('test.7z'), separator='') == Path('test2.7z')
    assert increment_filename_version(
        Path('test 10.7z'), separator='') == Path('test 102.7z')
