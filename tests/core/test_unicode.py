import pytest

from conftest import make_files, read_files
from organize import core


@pytest.mark.skip(reason="TODO")
def test_normalization_regex(testfs):
    make_files(
        testfs,
        {b"Ertra\xcc\x88gnisaufstellung.txt".decode("utf-8"): ""},
    )
    config = (
        b"""
    rules:
      - locations: "."
        filters:
          - regex: 'Ertra\xc3\xa4gnisaufstellung.txt$'
        actions:
          - rename: "found-regex.txt"
    """
    ).decode("utf-8")
    core.run(config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {"found-regex.txt"}


@pytest.mark.skip(reason="TODO")
def test_normalization_filename(testfs):
    make_files(
        testfs,
        {b"Ertr\xcc\x88gnisaufstellung.txt".decode("utf-8"): ""},
    )
    config = (
        b"""
    rules:
      - locations: "."
        filters:
          - filename: "Ertr\xc3\xa4gnisaufstellung"
        actions:
          - rename: "found-regex.txt"
    """
    ).decode("utf-8")
    core.run(config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {"found-regex.txt"}
