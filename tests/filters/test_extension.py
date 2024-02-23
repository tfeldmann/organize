from pathlib import Path

import pytest
from conftest import make_files

from organize import Config
from organize.filters.extension import Extension


@pytest.mark.parametrize(
    "path,match,suffix",
    (
        ("/somefile.pdf", True, "pdf"),
        ("/home/test/somefile.pdf.jpeg", False, "jpeg"),
        ("/home/test/gif.TXT", False, "txt"),
        ("/home/test/txt.GIF", True, "gif"),
        ("/somefile.pdf", True, "pdf"),
    ),
)
def test_extension(path, match, suffix):
    extension = Extension(["JPG", ".gif", "pdf"])
    suffix, match = extension.suffix_match(Path(path))
    assert match == match
    assert suffix == suffix


def test_extension_empty():
    suffix, match = Extension().suffix_match(Path("any.txt"))
    assert suffix == "txt"
    assert match


def test_filename_move(fs, testoutput):
    files = {
        "test.jpg": "",
        "asd.JPG": "",
        "nomatch.jpg.zip": "",
        "camel.jPeG": "",
    }
    make_files(files, "test")
    config = """
        rules:
        - locations: /test
          filters:
            - name
            - extension:
              - .jpg
              - jpeg
          actions:
            - echo: 'Found JPG file: {name}'
        """
    Config.from_string(config).execute(simulate=False, output=testoutput)
    assert testoutput.messages == [
        "Found JPG file: asd",
        "Found JPG file: camel",
        "Found JPG file: test",
    ]
