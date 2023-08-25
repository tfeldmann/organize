import fs
import pytest
from conftest import read_files

from organize.actions._conflict_resolution import (
    next_free_name,
    resolve_overwrite_conflict,
)
from organize.utils import Template


@pytest.mark.parametrize(
    "template,wanted,result",
    (
        ("{name}-{counter}{extension}", "file.txt", "file-2.txt"),
        ("{name}-{counter}{extension}", "file.txt", "file-2.txt"),
        ("{name}-{'%02d' % counter}{extension}", "file.txt", "file-03.txt"),
        ("{name}{counter}{extension}", "file.txt", "file4.txt"),
        ("{name}{counter}{extension}", "other.txt", "other.txt"),
    ),
)
def test_next_free_name(template, wanted, result):
    with fs.open_fs("mem://") as mem:
        mem.touch("file.txt")
        mem.touch("file1.txt")
        mem.touch("file-01.txt")
        mem.touch("file-02.txt")
        mem.touch("file2.txt")
        mem.touch("file3.txt")
        name, ext = fs.path.splitext(wanted)
        tmp = Template.from_string(template)
        assert next_free_name(mem, tmp, name, ext) == result


def test_next_free_name_exception():
    with fs.open_fs("mem://") as mem:
        mem.touch("file.txt")
        mem.touch("file1.txt")
        tmp = Template.from_string("{name}{extension}")
        with pytest.raises(ValueError):
            assert next_free_name(fs=mem, template=tmp, name="file", extension=".txt")


@pytest.mark.parametrize(
    "mode,result,files",
    (
        ("skip", None, {"file.txt": "file", "other.txt": "other"}),
        ("overwrite", "other.txt", {"file.txt": "file"}),
        # ("trash", None, {"file.txt": "file", "other.txt": "other"}),
        ("rename_new", "other2.txt", {"file.txt": "file", "other.txt": "other"}),
        ("rename_existing", "other.txt", {"file.txt": "file", "other2.txt": "other"}),
    ),
)
def test_resolve_overwrite_conflict(mode, result, files):
    with fs.open_fs("mem://") as mem:
        mem.writetext("file.txt", "file")
        mem.writetext("other.txt", "other")
        assert result == resolve_overwrite_conflict(
            src_fs=mem,
            src_path="file.txt",
            dst_fs=mem,
            dst_path="other.txt",
            conflict_mode=mode,
            rename_template=Template.from_string("{name}{counter}{extension}"),
            simulate=False,
            print=print,
        )
        assert files == read_files(mem)
