from fs import open_fs
from fs.memoryfs import MemoryFS
from organize.utils import is_same_resource


def test_mem():
    a = open_fs("mem://")
    a.touch("file1")
    b = a.makedir("b")
    b.touch("file2")
    c = a

    assert is_same_resource(a, "b/file2", a, "b/file2")
    assert is_same_resource(a, "b/file2", b, "file2")
    assert is_same_resource(a, "file1", c, "file1")


def test_mem2():
    mem = MemoryFS()
    fs1, path1 = mem.makedir("files"), "test.txt"
    fs2, path2 = mem, "files/test.txt"

    assert is_same_resource(fs1, path1, fs2, path2)


def test_osfs():
    a = open_fs("~/Desktop")
    b = open_fs("~/")
    c = b.opendir("Desktop")

    assert is_same_resource(a, "file.txt", a, "file.txt")
    assert is_same_resource(a, "file.txt", b, "Desktop/file.txt")
    assert is_same_resource(a, "file.txt", c, "file.txt")


def test_inter():
    a = open_fs("temp://")
    b = open_fs(a.getsyspath("/"))
    a_dir = a.makedir("a")

    assert is_same_resource(a, "test.txt", b, "test.txt")
    assert is_same_resource(b, "a/subfile.txt", a_dir, "subfile.txt")
    # assert is_same_resource(a, "test.txt", a_dir, "../test.txt")
