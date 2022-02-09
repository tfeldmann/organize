from conftest import assertdir, create_filesystem

from organize.cli import main


def test_rename_files_date(tmp_path):
    # inspired by https://github.com/tfeldmann/organize/issues/43
    create_filesystem(
        tmp_path,
        files=[
            "File_abc_dat20190812_xyz.pdf",
            "File_xyz_bar19990101_a.pdf",
            "File_123456_foo20000101_xyz20190101.pdf",
        ],
        config=r"""
        rules:
        - folders: files
          filters:
            - regex: 'File_.*?(?P<y>\d{4})(?P<m>\d{2})(?P<d>\d{2}).*?.pdf'
          actions:
            - rename: "File_{regex.d}{regex.m}{regex.y}.pdf"
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "File_12082019.pdf", "File_01011999.pdf", "File_01012000.pdf")
