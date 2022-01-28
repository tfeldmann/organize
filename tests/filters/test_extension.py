from fs import open_fs
from fs.path import dirname
from organize.filters import Extension


def test_extension():
    extension = Extension("JPG", ".gif", "pdf")
    testpathes = [
        ("/somefile.pdf", True),
        ("/home/test/somefile.pdf.jpeg", False),
        ("/home/test/gif.TXT", False),
        ("/home/test/txt.GIF", True),
        ("/somefile.pdf", True),
    ]
    with open_fs("mem://", writeable=True, create=True) as mem:
        for f, match in testpathes:
            mem.makedirs(dirname(f), recreate=True)
            mem.touch(f)
            assert extension.run(fs=mem, fs_path=f).matches == match


def test_extension_empty():
    fs = open_fs("mem://")
    fs.touch("test.txt")
    extension = Extension()
    assert extension.run(fs=fs, fs_path="test.txt").matches


def test_extension_result():
    path = "~/somefile.TxT"
    extension = Extension("txt")
    assert extension.matches(path)
    result = extension.run(path=path)["extension"]
    assert str(result) == "TxT"
    assert result.lower == "txt"
    assert result.upper == "TXT"

    extension = Extension(".txt")
    assert extension.matches(path)
    result = extension.run(path=path)["extension"]
    assert str(result) == "TxT"
    assert result.lower == "txt"
    assert result.upper == "TXT"
