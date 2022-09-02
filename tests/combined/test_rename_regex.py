import pytest
from conftest import make_files, read_files

from organize import core


@pytest.mark.parametrize("loc", (".", "/"))
def test_rename_files_date(testfs, loc):
    # inspired by https://github.com/tfeldmann/organize/issues/43
    files = {
        "File_abc_dat20190812_xyz.pdf": "",
        "File_xyz_bar19990101_a.pdf": "",
        "File_123456_foo20000101_xyz20190101.pdf": "",
    }
    make_files(testfs, files)
    config = (
        r"""
    rules:
    - locations: "%s"
      filters:
        - regex: 'File_.*?(?P<y>\d{4})(?P<m>\d{2})(?P<d>\d{2}).*?.pdf'
      actions:
        - rename: "File_{regex.d}{regex.m}{regex.y}.pdf"
    """
        % loc
    )
    core.run(config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {
        "File_12082019.pdf": "",
        "File_01011999.pdf": "",
        "File_01012000.pdf": "",
    }
