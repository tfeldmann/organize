from mock import call

from conftest import create_filesystem
from organize.cli import main


def test_size_zero(tmp_path, mock_echo):
    create_filesystem(
        tmp_path,
        files=["1", "2", "3"],
        config="""
        rules:
        - folders: files
          filters:
            - filesize: 0
          actions:
            - echo: '{path.name}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    mock_echo.assert_has_calls((call("1"), call("2"), call("3")), any_order=True)


def test_basic(tmp_path, mock_echo):
    create_filesystem(
        tmp_path,
        files=["empty", "full", "halffull", "two_thirds.txt"],
        config="""
        rules:
        - folders: files
          filters:
            - filesize: '> 1kb, <= 1.0 KiB'
          actions:
            - echo: '{path.name} {filesize.bytes} ({filesize.conditions})'
        - folders: files
          filters:
            - filesize:
              - '> 0.5 kb'
              - '<1.0 KiB'
          actions:
            - echo: '2/3 {filesize.bytes} ({filesize.conditions})'
        """,
    )
    with open(tmp_path / "files" / "halffull", "w") as h:
        h.write("0" * 1010)
    with open(tmp_path / "files" / "full", "w") as h:
        h.write("0" * 2000)
    with open(tmp_path / "files" / "two_thirds", "w") as h:
        h.write("0" * 666)
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    mock_echo.assert_has_calls(
        [
            call("halffull 1010 (> 1kb, <= 1.0 KiB)"),
            call("2/3 666 (> 0.5 kb, <1.0 KiB)"),
        ],
        any_order=True,
    )
