from typing import Callable, Tuple, Union, NamedTuple

from fs.base import FS
from fs.move import move_dir, move_file
from fs.path import splitext
from jinja2 import Template

from organize.utils import file_desc, next_free_name

from .trash import Trash

CONFLICT_OPTIONS = (
    "skip",
    "overwrite",
    "trash",
    "rename_new",
    "rename_existing",
    # "keep_newer",
    # "keep_older",
)


class ResolverResult(NamedTuple):
    dst_fs: FS
    dst_path: str
    skip: bool


def resolve_overwrite_conflict(
    dst_fs: FS,
    dst_path: str,
    conflict_mode: str,
    rename_template: Template,
    simulate: bool,
    print: Callable,
) -> ResolverResult:
    if conflict_mode == "trash":
        Trash().pipeline({"fs": dst_fs, "fs_path": dst_path}, simulate=simulate)
        return ResolverResult(dst_fs=dst_fs, dst_path=dst_path, skip=False)

    elif conflict_mode == "skip":
        print("Skipped.")
        return ResolverResult(dst_fs=dst_fs, dst_path=dst_path, skip=True)

    elif conflict_mode == "overwrite":
        print("Overwrite %s." % file_desc(dst_fs, dst_path))
        return ResolverResult(dst_fs=dst_fs, dst_path=dst_path, skip=False)

    elif conflict_mode == "rename_new":
        stem, ext = splitext(dst_path)
        name = next_free_name(
            fs=dst_fs,
            name=stem,
            extension=ext,
            template=rename_template,
        )
        return ResolverResult(dst_fs=dst_fs, dst_path=name, skip=False)

    elif conflict_mode == "rename_existing":
        stem, ext = splitext(dst_path)
        name = next_free_name(
            fs=dst_fs,
            name=stem,
            extension=ext,
            template=rename_template,
        )
        print('Renaming existing to: "%s"' % name)
        if not simulate:
            if dst_fs.isdir(dst_path):
                move_dir(dst_fs, dst_path, dst_fs, name)
            elif dst_fs.isfile(dst_path):
                move_file(dst_fs, dst_path, dst_fs, name)

        return ResolverResult(dst_fs=dst_fs, dst_path=dst_path, skip=False)
