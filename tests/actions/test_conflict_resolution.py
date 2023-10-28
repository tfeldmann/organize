from pathlib import Path

import pytest
from conftest import make_files, read_files

from organize.actions.common.conflict import (
    next_free_name,
    resolve_conflict,
)
from organize.output import RawOutput
from organize.resource import Resource
from organize.template import Template


@pytest.mark.parametrize(
    "template,wanted,result",
    (
        ("{name}-{counter}{extension}", "file.txt", "file-2.txt"),
        ("{name}-{counter}{extension}", "file.txt", "file-2.txt"),
        (r"{name}-{'%02d' % counter}{extension}", "file.txt", "file-03.txt"),
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


@pytest.mark.parametrize(
    "mode,result,files",
    (
        (
            "skip",
            (True, "test/file.txt"),
            {"file.txt": "file", "other.txt": "other"},
        ),
        (
            "overwrite",
            (False, "test/other.txt"),
            {"file.txt": "file"},
        ),
        # ("trash", None, {"file.txt": "file", "other.txt": "other"}),
        (
            "rename_new",
            (False, "test/other2.txt"),
            {"file.txt": "file", "other.txt": "other"},
        ),
        (
            "rename_existing",
            (False, "test/other.txt"),
            {"file.txt": "file", "other2.txt": "other"},
        ),
    ),
)
def test_resolve_overwrite_conflict(fs, mode, result, files):
    make_files(
        {
            "file.txt": "file",
            "other.txt": "other",
        },
        "test",
    )
    output = RawOutput()
    skip_action, use_dst = resolve_conflict(
        dst=Path("test/other.txt"),
        res=Resource(path=Path("test/file.txt")),
        conflict_mode=mode,
        rename_template=Template.from_string("{name}{counter}{extension}"),
        simulate=False,
        output=output,
    )
    assert (skip_action, use_dst) == (result[0], Path(result[1]))
    assert files == read_files("test")


def test_conflicting_folders(fs):
    make_files({"src": {}, "dir1": {"sub1": {}, "sub2": {}}}, "test")
    result = resolve_conflict(
        dst=Path("/test/dir1/sub1"),
        res=Resource(path=Path("/test/src")),
        rename_template=Template.from_string("{name} {counter}{extension}"),
        conflict_mode="rename_new",
        simulate=False,
        output=RawOutput(),
    )
    assert not result.skip_action
    assert result.use_dst == Path("/test/dir1/sub1 2")
