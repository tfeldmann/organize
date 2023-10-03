from pathlib import Path

import pytest
from conftest import read_files

from organize.actions.common.conflict import next_free_name
from organize.utils import Template


@pytest.mark.parametrize(
    "template,wanted,result",
    (
        ("{name}-{counter}{extension}", "file.txt", "file-2.txt"),
        ("{name}-{counter}{extension}", "file.txt", "file-2.txt"),
        ("{name}-{'%02d' % counter}{extension}", "file.txt", "file-03.txt"),
        ("{name}{counter}{extension}", "file.txt", "file4.txt"),
        ("{name}{counter}{extension}", "other.txt", "other.txt"),
        ("{name} {counter}{extension}", "folder/test.txt", "folder/test 2.txt"),
        ("{name} {counter}{extension}", "folder/other.txt", "folder/other.txt"),
    ),
)
def test_next_free_name(fs, template, wanted, result):
    fs.create_file("file.txt")
    fs.create_file("file1.txt")
    fs.create_file("file-01.txt")
    fs.create_file("file-02.txt")
    fs.create_file("file2.txt")
    fs.create_file("file3.txt")
    fs.create_file("folder/test.txt")

    tmp = Template.from_string(template)
    assert next_free_name(dst=Path(wanted), template=tmp) == Path(result)


def test_next_free_name_exception(fs):
    fs.create_file("file.txt")
    fs.create_file("file1.txt")
    tmp = Template.from_string("{name}{extension}")
    with pytest.raises(ValueError):
        assert next_free_name(dst=Path("file.txt"), template=tmp)


# @pytest.mark.parametrize(
#     "mode,result,files",
#     (
#         ("skip", None, {"file.txt": "file", "other.txt": "other"}),
#         ("overwrite", "other.txt", {"file.txt": "file"}),
#         # ("trash", None, {"file.txt": "file", "other.txt": "other"}),
#         ("rename_new", "other2.txt", {"file.txt": "file", "other.txt": "other"}),
#         ("rename_existing", "other.txt", {"file.txt": "file", "other2.txt": "other"}),
#     ),
# )
# def test_resolve_overwrite_conflict(mode, result, files):
#     with fs.open_fs("mem://") as mem:
#         mem.writetext("file.txt", "file")
#         mem.writetext("other.txt", "other")
#         assert result == resolve_overwrite_conflict(
#             src_fs=mem,
#             src_path="file.txt",
#             dst_fs=mem,
#             dst_path="other.txt",
#             conflict_mode=mode,
#             rename_template=Template.from_string("{name}{counter}{extension}"),
#             simulate=False,
#             print=print,
#         )
#         assert files == read_files(mem)
