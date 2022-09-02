from typing import Callable, Union

import jinja2
from fs import errors, open_fs
from fs.base import FS
from fs.move import move_dir, move_file
from fs.opener.errors import OpenerError
from fs.path import basename, dirname, join, splitext
from jinja2 import Template

from organize.utils import expand_args, is_same_resource, safe_description

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


def next_free_name(fs: FS, template: jinja2.Template, name: str, extension: str) -> str:
    """
    Increments {counter} in the template until the given resource does not exist.

    Args:
        fs (FS): the filesystem to work on
        template (jinja2.Template):
            A jinja2 template with placeholders for {name}, {extension} and {counter}
        name (str): The wanted filename
        extension (str): the wanted extension

    Raises:
        ValueError if no free name can be found with the given template.so

    Returns:
        (str) A filename according to the given template that does not exist on **fs**.
    """
    counter = 1
    prev_candidate = ""
    if not extension.startswith("."):
        extension = ".%s" % extension
    wanted = "%s%s" % (name, extension)
    if not fs.exists(wanted):
        return wanted
    while True:
        candidate = template.render(name=name, extension=extension, counter=counter)
        if not fs.exists(candidate):
            return candidate
        if prev_candidate == candidate:
            raise ValueError(
                "Could not find a free filename for the given template. "
                'Maybe you forgot the "{counter}" placeholder?'
            )
        prev_candidate = candidate
        counter += 1


def resolve_overwrite_conflict(
    src_fs: FS,
    src_path: str,
    dst_fs: FS,
    dst_path: str,
    conflict_mode: str,
    rename_template: Template,
    simulate: bool,
    print: Callable,
) -> Union[None, str]:
    """
    Returns:
        - A new path if applicable
        - None if this action should be skipped.
    """
    if is_same_resource(src_fs, src_path, dst_fs, dst_path):
        print("Same resource: Skipped.")
        return None

    if conflict_mode == "trash":
        Trash().run(fs=dst_fs, fs_path=dst_path, simulate=simulate)
        return dst_path

    elif conflict_mode == "skip":
        print("Skipped.")
        return None

    elif conflict_mode == "overwrite":
        print("Overwrite %s." % safe_description(dst_fs, dst_path))
        if not simulate:
            if dst_fs.isdir(dst_path):
                dst_fs.removedir(dst_path)
            elif dst_fs.isfile(dst_path):
                dst_fs.remove(dst_path)
        return dst_path

    elif conflict_mode == "rename_new":
        stem, ext = splitext(dst_path)
        name = next_free_name(
            fs=dst_fs,
            name=stem,
            extension=ext,
            template=rename_template,
        )
        return name

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
        return dst_path

    raise ValueError("Unknown conflict_mode %s" % conflict_mode)


def dst_from_options(src_path, dest, filesystem, args: dict):
    # append the original resource name if destination is a dir (ends with "/")
    dst_path = expand_args(dest, args)
    if dst_path.endswith(("\\", "/")):
        dst_path = join(dst_path, basename(src_path))

    if filesystem:
        if isinstance(filesystem, str):
            dst_fs = expand_args(filesystem, args)
        else:
            dst_fs = filesystem
    else:
        dst_fs = dirname(dst_path)
        dst_path = basename(dst_path)
    return dst_fs, dst_path


def check_conflict(
    src_fs: FS,
    src_path: str,
    dst_fs: FS,
    dst_path: str,
    conflict_mode: str,
    rename_template: Template,
    simulate: bool,
    print: Callable,
):
    skip = False
    try:
        check_fs = open_fs(dst_fs, create=False, writeable=True)
        if check_fs.exists(dst_path):
            print(
                '%s already exists! (conflict mode is "%s").'
                % (safe_description(dst_fs, dst_path), conflict_mode)
            )
            new_path = resolve_overwrite_conflict(
                src_fs=src_fs,
                src_path=src_path,
                dst_fs=check_fs,
                dst_path=dst_path,
                conflict_mode=conflict_mode,
                rename_template=rename_template,
                simulate=simulate,
                print=print,
            )
            if new_path is not None:
                dst_path = new_path
            else:
                skip = True
    except (errors.CreateFailed, OpenerError):
        pass

    return skip, dst_path
