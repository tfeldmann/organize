import pytest
from conftest import make_files, read_files

from organize import Config
from organize.filters.filetype import file_group


@pytest.mark.parametrize(
    "name, group",
    [
        ("report.PDF", "Documents"),
        ("photo.heic", "Images"),
        ("budget.xlsx", "Spreadsheets"),
        ("movie.mkv", "Videos"),
        ("setup.dmg", "Installers"),
        ("backup.tar.gz", "Archives"),
        ("song.mp3", "Audio"),
        ("unknown.qwertz", "Other"),
        ("README", "Other"),
    ],
)
def test_file_group(name, group):
    assert file_group(name) == group


def test_sort_by_type(fs):
    make_files(["a.jpg", "b.zip", "c.pdf", "d.qwertz"], "test")
    Config.from_string(
        """
        rules:
          - locations: "/test"
            filters:
              - filetype
            actions:
              - move: "/sorted/{filetype}/"
        """
    ).execute(simulate=False)
    assert read_files("sorted") == {
        "Images": {"a.jpg": ""},
        "Archives": {"b.zip": ""},
        "Documents": {"c.pdf": ""},
        "Other": {"d.qwertz": ""},
    }


def test_filter_by_type(fs):
    make_files(["a.jpg", "b.zip", "c.png"], "test")
    Config.from_string(
        """
        rules:
          - locations: "/test"
            filters:
              - filetype: images
            actions:
              - move: "/images/"
        """
    ).execute(simulate=False)
    assert read_files("images") == {"a.jpg": "", "c.png": ""}
    assert read_files("test") == {"b.zip": ""}
