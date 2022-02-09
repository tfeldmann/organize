import pytest
from conftest import assertdir, create_filesystem

from organize.cli import main


@pytest.mark.skip(reason="Todo")
def test_normalization_regex(tmp_path):
    create_filesystem(
        tmp_path,
        files=[b"Ertra\xcc\x88gnisaufstellung.txt".decode("utf-8")],
        config="""
            rules:
              - folders: files
                filters:
                  - regex: '^{}$'
                actions:
                  - rename: "found-regex.txt"
        """.format(
            b"Ertr\xc3\xa4gnisaufstellung\\.txt".decode("utf-8")
        ),
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "found-regex.txt")


@pytest.mark.skip(reason="Todo")
def test_normalization_glob(tmp_path):
    create_filesystem(
        tmp_path,
        files=[b"Ertra\xcc\x88gnisaufstellung.txt".decode("utf-8")],
        config="""
            rules:
                - folders: ./**/{}.*
                  actions:
                    - rename: "found-glob.txt"
        """.format(
            b"Ertr\xc3\xa4gnisaufstellung".decode("utf-8")
        ),
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "found-glob.txt")


@pytest.mark.skip(reason="Todo")
def test_normalization_filename(tmp_path):
    create_filesystem(
        tmp_path,
        files=[b"Ertra\xcc\x88gnisaufstellung.txt".decode("utf-8")],
        config="""
            rules:
                - folders: files
                  filters:
                    - filename:
                        contains: {}
                  actions:
                    - rename: "found-filename.txt"
        """.format(
            b"Ertr\xc3\xa4gnisaufstellung".decode("utf-8")
        ),
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(tmp_path, "found-filename.txt")
