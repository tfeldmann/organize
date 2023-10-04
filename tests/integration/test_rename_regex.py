from conftest import make_files, read_files

from organize import Config


def test_rename_files_date(fs):
    # inspired by https://github.com/tfeldmann/organize/issues/43
    files = {
        "File_abc_dat20190812_xyz.pdf": "",
        "File_xyz_bar19990101_a.pdf": "",
        "File_123456_foo20000101_xyz20190101.pdf": "",
    }
    make_files(files, path="test")
    config = r"""
    rules:
    - locations: "test"
      filters:
        - regex: 'File_.*?(?P<y>\d{4})(?P<m>\d{2})(?P<d>\d{2}).*?.pdf'
      actions:
        - rename: "File_{regex.d}{regex.m}{regex.y}.pdf"
    """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {
        "File_12082019.pdf": "",
        "File_01011999.pdf": "",
        "File_01012000.pdf": "",
    }
