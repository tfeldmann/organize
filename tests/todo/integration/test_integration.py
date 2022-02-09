import pytest
from conftest import assertdir, create_filesystem

from organize.cli import main


def test_filename_move(tmp_path):
    create_filesystem(
        tmp_path,
        files=["test.PY"],
        config="""
            rules:
            - folders: files
              filters:
              - Extension
              actions:
              - rename: '{path.stem}{path.stem}.{extension.lower}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "testtest.py")


def test_basic(tmp_path):
    create_filesystem(
        tmp_path,
        files=["asd.txt", "newname 2.pdf", "newname.pdf", "test.pdf"],
        config="""
            rules:
            - folders: files
              filters:
                - filename: test
              actions:
                - copy: files/newname.pdf
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path, "newname.pdf", "newname 2.pdf", "newname 3.pdf", "test.pdf", "asd.txt"
    )


def test_globstr(tmp_path):
    create_filesystem(
        tmp_path,
        files=["asd.txt", "newname 2.pdf", "newname.pdf", "test.pdf"],
        config="""
            rules:
              - folders: 'file[s]/*.pdf'
                actions:
                  - delete
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "asd.txt")


@pytest.mark.skip(reason="Todo")
def test_dependent_rules(tmp_path):
    create_filesystem(
        tmp_path,
        files=["asd.txt", "newname 2.pdf", "newname.pdf", "test.pdf"],
        config="""
            rules:
            - folders: files
              filters:
                - filename: test
              actions:
                - copy: files/newfolder/test.pdf

            - folders: files/newfolder/
              filters:
                - filename: test
              actions:
                - rename: test-found.pdf
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path,
        "newname.pdf",
        "newname 2.pdf",
        "test.pdf",
        "asd.txt",
        "newfolder/test-found.pdf",
    )
