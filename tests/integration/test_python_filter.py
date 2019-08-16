from mock import call

from conftest import assertdir, create_filesystem
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
                return int(path.name.split('.')[0][-2:]) * 100
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


def test_odd_detector(tmp_path, mock_echo):
    create_filesystem(
        tmp_path,
        files=["student-01.txt", "student-02.txt", "student-03.txt", "student-04.txt"],
        config="""
        rules:
        - folders: files
          filters:
            - python: |
                return int(path.stem.split('-')[1]) % 2 == 1
          actions:
            - echo: 'Odd student numbers: {path.name}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    mock_echo.assert_has_calls(
        (
            call("Odd student numbers: student-01.txt"),
            call("Odd student numbers: student-03.txt"),
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
                    "name": path.name[:3],
                    "code": int(path.name.split('.')[0][-2:]) * 100,
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

def test_name_reverser(tmp_path):
    create_filesystem(
        tmp_path,
        files=["desrever.jpg", "emanelif.txt"],
        config="""
        rules:
          - folders: files
            filters:
            - extension
            - python: |
                return {
                    "reversed_name": path.stem[::-1],
                }
            actions:
            - rename: '{python.reversed_name}.{extension}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "reversed.jpg", "filename.txt")
