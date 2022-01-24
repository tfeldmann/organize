import os
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any, Hashable, List, Sequence, Union

from fs.base import FS
from fs.errors import NoSysPath
from jinja2 import Environment, Template

JinjaEnv = Environment(
    variable_start_string="{",
    variable_end_string="}",
    finalize=lambda x: x() if callable(x) else x,
    autoescape=False,
)


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


def next_free_name(fs: FS, template: Template, name: str, extension: str) -> str:
    counter = 1
    prev_candidate = ""
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


def ensure_list(inp):
    if not isinstance(inp, list):
        return [inp]
    return inp
