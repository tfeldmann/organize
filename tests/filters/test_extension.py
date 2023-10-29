from pathlib import Path
from unittest.mock import call

from conftest import make_files

from organize import Config
from organize.filters.extension import Extension, process
from organize.resource import Resource


def test_extension(msg_output):
    extension = Extension(["JPG", ".gif", "pdf"])
    testpathes = [
        ("/somefile.pdf", True),
        ("/home/test/somefile.pdf.jpeg", False),
        ("/home/test/gif.TXT", False),
        ("/home/test/txt.GIF", True),
        ("/somefile.pdf", True),
    ]
    for f, match in testpathes:
        res = Resource(path=Path(f))
        result = extension.pipeline(res=res, output=msg_output)
        assert result == match


def test_extension_empty():
    with open_fs("mem://") as mem:
        mem.touch("test.txt")
        extension = Extension()
        assert extension.run(fs=mem, fs_path="test.txt").matches


def test_extension_result():
    with open_fs("mem://") as mem:
        path = "somefile.TxT"
        mem.touch(path)

        extension = Extension("txt")
        assert extension.matches(".TxT")
        result = extension.run(fs=mem, fs_path=path).updates["extension"]
        assert str(result) == "TxT"
        assert result.lower() == "txt"
        assert result.upper() == "TXT"

        extension = Extension(".txt")
        assert extension.matches(".TXT")
        result = extension.run(fs=mem, fs_path=path).updates["extension"]
        assert str(result) == "TxT"
        assert result.lower() == "txt"
        assert result.upper() == "TXT"


def test_filename_move(testfs, mock_echo):
    files = {
        "test.jpg": "",
        "asd.JPG": "",
        "nomatch.jpg.zip": "",
        "camel.jPeG": "",
    }
    make_files(testfs, files)
    config = """
        rules:
        - locations: "."
          filters:
            - name
            - extension:
              - .jpg
              - jpeg
          actions:
            - echo: 'Found JPG file: {name}'
        """
    core.run(config, simulate=False, working_dir=testfs)
    mock_echo.assert_has_calls(
        (
            call("Found JPG file: test"),
            call("Found JPG file: asd"),
            call("Found JPG file: camel"),
        ),
        any_order=True,
    )
