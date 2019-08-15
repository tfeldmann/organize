from mock import call

from conftest import create_filesystem
from organize.cli import main


def test_python(tmp_path, mock_echo):
    create_filesystem(
        tmp_path,
        files=["student-01.jpg", "student-01.txt", "student-02.txt", "student-03.txt"],
        config="""
        rules:
        - folders: files
          filters:
            - extension: txt
            - python: |
                return int(args.path.name.split('.')[0][-2:]) * 100
          actions:
            - echo: '{python}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    mock_echo.assert_has_calls(
        (
            call("100"),
            call("200"),
            call("300"),
        ),
        any_order=True,
    )


def test_python_dict(tmp_path, mock_echo):
    create_filesystem(
        tmp_path,
        files=["foo-01.jpg", "foo-01.txt", "bar-02.txt", "baz-03.txt"],
        config="""
        rules:
          - folders: files
            filters:
            - extension: txt
            - python: |
                return {
                    "name": args.path.name[:3],
                    "code": int(args.path.name.split('.')[0][-2:]) * 100,
                }
            actions:
            - echo: '{python.code} {python.name}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    mock_echo.assert_has_calls(
        (
            call("100 foo"),
            call("200 bar"),
            call("300 baz"),
        ),
        any_order=True,
    )
