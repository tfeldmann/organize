import fs
import pytest

from organize.actions._conflict_resolution import next_free_name
from organize.utils import Template


@pytest.mark.parametrize(
    "template,wanted,result",
    (
        ("{name}-{counter}.{extension}", "file.txt", "file-1.txt"),
        ("{name}{counter}.{extension}", "file.txt", "file4.txt"),
        ("{name}{counter}.{extension}", "other.txt", "other.txt"),
    ),
)
def test_next_free_name(template, wanted, result):
    with fs.open_fs("mem://") as mem:
        mem.touch("file.txt")
        mem.touch("file1.txt")
        mem.touch("file2.txt")
        mem.touch("file3.txt")
        name, ext = wanted.split(".")
        tmp = Template.from_string(template)
        assert next_free_name(mem, tmp, name, ext) == result


def test_next_free_name_exception():
    with fs.open_fs("mem://") as mem:
        mem.touch("file.txt")
        mem.touch("file1.txt")
        tmp = Template.from_string("{name}.{extension}")
        with pytest.raises(ValueError):
            assert next_free_name(mem, tmp, "file", "txt")
