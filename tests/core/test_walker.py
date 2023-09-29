from organize.walker import Walker


def test_location(fs):
    fs.create_file("test/folder/file.txt")
    fs.create_file("test/folder/subfolder/another.pdf")
    fs.create_file("test/hi/there")
    fs.create_file("test/hi/.other")
    fs.create_file("test/.hidden/some.pdf")

    assert list(Walker().files("test")) == [
        "test/folder/file.txt",
        "test/folder/subfolder/another.pdf",
        "test/hi/there",
        "test/hi/.other",
        "test/.hidden/some.pdf",
    ]
    assert list(Walker(method="depth").files("test")) == [
        "test/folder/subfolder/another.pdf",
        "test/folder/file.txt",
        "test/hi/there",
        "test/hi/.other",
        "test/.hidden/some.pdf",
    ]
