import os
import re
from copy import deepcopy
from datetime import datetime
from typing import Any, List, Sequence, Tuple, Union

import jinja2
from fs import open_fs
from fs import path as fspath
from fs.base import FS
from fs.memoryfs import MemoryFS
from jinja2 import nativetypes


def ensure_list(inp):
    if not isinstance(inp, list):
        return [inp]
    return inp


def ensure_dict(inp):
    if isinstance(inp, dict):
        return inp
    elif isinstance(inp, str):
        return {inp: {}}
    raise ValueError("Cannot ensure dict: %s" % inp)


def to_args(inp):
    """Convert a argument into a (args, kwargs) tuple.

    >>> to_args(None)
    ([], {})
    >>> to_args('test')
    (['test'], {})
    >>> to_args([1, 2, 3])
    ([1, 2, 3], {})
    >>> to_args({'a': {'b': 'c'}})
    ([], {'a': {'b': 'c'}})
    >>> to_args([[1, 2, [3, 4], [5, 6]]])
    ([1, 2, 3, 4, 5, 6], {})
    """
    if inp is None:
        return ([], {})
    if isinstance(inp, dict):
        return ([], inp)
    return (flatten(ensure_list(inp)), {})


def flattened_string_list(x, case_sensitive=True) -> Sequence[str]:
    x = [str(x) for x in flatten(x)]
    if not case_sensitive:
        x = [x.lower() for x in x]
    return x


def flatten_all_lists_in_dict(obj):
    """
    >>> flatten_all_lists_in_dict({1: [[2], [3, {5: [5, 6]}]]})
    {1: [2, 3, {5: [5, 6]}]}
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = flatten_all_lists_in_dict(value)
        return obj
    elif isinstance(obj, list):
        return [flatten_all_lists_in_dict(x) for x in flatten(obj)]
    else:
        return obj


def deep_merge(a: dict, b: dict, *, add_keys=True) -> dict:
    result = deepcopy(a)
    for bk, bv in b.items():
        av = result.get(bk)
        if isinstance(av, dict) and isinstance(bv, dict):
            result[bk] = deep_merge(av, bv, add_keys=add_keys)
        elif (av is not None) or add_keys:
            result[bk] = deepcopy(bv)
    return result


def deep_merge_inplace(base: dict, updates: dict) -> None:
    for bk, bv in updates.items():
        av = base.get(bk)
        if isinstance(av, dict) and isinstance(bv, dict):
            deep_merge_inplace(av, bv)
        else:
            base[bk] = bv
