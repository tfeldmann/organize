from typing import Text
import fs

from organize.rule import Rule, PatternWalker


def create_file(filesystem: "fs.base.FS", path: Text, contents: Text = ""):
    dirs = fs.path.dirname(path)
    filesystem.makedirs(dirs)
    filesystem.writetext(path=path, contents=contents)


def list_files(filesystem: "fs.base.FS", pattern: Text):
    walker = PatternWalker(pattern=pattern)
    for f in walker.files(filesystem):
        yield f


def test_matching():
    with fs.open_fs("mem://") as mem_fs:
        create_file(mem_fs, "/Pictures/2020/Vacation/journal.txt")
        create_file(mem_fs, "/Pictures/2020/Work/text.txt")
        create_file(mem_fs, "/Pictures/2019/Vacation/text.txt")
        create_file(mem_fs, "/Pictures/2019/Work/text.txt")
        create_file(mem_fs, "/Documents/Office/Taxes/text.txt")
        create_file(mem_fs, "/Documents/Office/Invoices/text.txt")
        create_file(mem_fs, "/Documents/Private/Invoices/text.txt")
        mem_fs.tree()
        print(list(list_files(mem_fs, "Pic*/**/*.txt")))
        assert False
