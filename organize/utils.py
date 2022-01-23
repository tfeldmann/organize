from fs.errors import NoSysPath
import os
import re
from collections.abc import Mapping
from copy import deepcopy
from functools import partial
from pathlib import Path
from typing import Any, Hashable, List, Sequence, Tuple, Union

from jinja2 import Template as JinjaTemplate

Template = partial(
    JinjaTemplate,
    variable_start_string="{",
    variable_end_string="}",
)

WILDCARD_REGEX = re.compile(r"(?<!\\)[\*\?\[]+")


def splitglob(globstr: str) -> Tuple[Path, str]:
    """split a string with wildcards into a base folder and globstring"""
    path = fullpath(globstr.strip())
    parts = path.parts
    for i, part in enumerate(parts):
        if WILDCARD_REGEX.search(part):
            return (Path(*parts[:i]), str(Path(*parts[i:])))
    return (path, "")


def fullpath(path: Union[str, Path]) -> Path:
    """Expand '~' and resolve the given path. Path can be a string or a Path obj."""
    return Path(os.path.expandvars(str(path))).expanduser().resolve(strict=False)


def flatten(arr: List[Any]) -> List[Any]:
    if arr == []:
        return []
    if not isinstance(arr, list):
        return [arr]
    return flatten(arr[0]) + flatten(arr[1:])


def flattened_string_list(x, case_sensitive=True) -> Sequence[str]:
    x = [str(x) for x in flatten(x)]
    if not case_sensitive:
        x = [x.lower() for x in x]
    return x


def first_key(dic: Mapping) -> Hashable:
    return list(dic.keys())[0]


def find_unused_filename(path: Path, separator=" ") -> Path:
    """
    We assume the given path already exists. This function adds a counter to the
    filename until we find a unused filename.
    """
    # TODO: Check whether the assumption can be eliminated for cleaner code.
    # TODO: Optimization: The counter only needs to be parsed once.
    tmp = path
    while True:
        tmp = increment_filename_version(tmp, separator=separator)
        if not tmp.exists():
            return tmp


def deep_merge(a: dict, b: dict) -> dict:
    result = deepcopy(a)
    for bk, bv in b.items():
        av = result.get("k")
        if isinstance(av, dict) and isinstance(bv, dict):
            result[bk] = deep_merge(av, bv)
        else:
            result[bk] = deepcopy(bv)
    return result


def deep_merge_inplace(base: dict, updates: dict) -> None:
    for bk, bv in updates.items():
        av = base.get("k")
        if isinstance(av, dict) and isinstance(bv, dict):
            deep_merge_inplace(av, bv)
        else:
            base[bk] = bv


def file_desc(fs, path):
    try:
        return fs.getsyspath(path)
    except NoSysPath:
        return "{} on {}".format(path, fs)
