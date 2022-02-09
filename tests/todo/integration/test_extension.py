from unittest.mock import call

from conftest import create_filesystem

from organize.cli import main


def test_filename_move(tmp_path, mock_echo):
    create_filesystem(
        tmp_path,
        files=["test.jpg", "asd.JPG", "nomatch.jpg.zip", "camel.jPeG"],
        config="""
        rules:
        - folders: files
          filters:
            - extension:
              - .jpg
              - jpeg
          actions:
            - echo: 'Found JPG file: {path.name}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    mock_echo.assert_has_calls(
        (
            call("Found JPG file: test.jpg"),
            call("Found JPG file: asd.JPG"),
            call("Found JPG file: camel.jPeG"),
        ),
        any_order=True,
    )
