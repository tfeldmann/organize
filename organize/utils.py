import os
import re
import sys
from collections.abc import Mapping
from copy import deepcopy

# in python < 3.6 the pathlib module misses some features so we have to import
# a backported alternative
if sys.version_info < (3, 6):
    from pathlib2 import Path
else:
    from pathlib import Path

WILDCARD_REGEX = re.compile(r"(?<!\\)[\*\?\[]+")


def splitglob(globstr):
    """ split a string with wildcards into a base folder and globstring """
    path = fullpath(globstr.strip())
    parts = path.parts
    for i, part in enumerate(parts):
        if WILDCARD_REGEX.search(part):
            return (Path(*parts[:i]), str(Path(*parts[i:])))
    return (path, "")


def fullpath(path):
    """ Expand '~' and resolve the given path """
    return Path(os.path.expandvars(path)).expanduser().resolve(strict=False)


def flatten(arr):
    if arr == []:
        return []
    if not isinstance(arr, list):
        return [arr]
    return flatten(arr[0]) + flatten(arr[1:])


def flattened_string_list(x, case_sensitive=True):
    if isinstance(x, str):
        x = [x]
    x = [str(x) for x in flatten(x)]
    if not case_sensitive:
        x = [x.lower() for x in x]
    return x


def first_key(dic: dict):
    return list(dic.keys())[0]


class DotDict(dict):
    """
    Quick and dirty implementation of a dot-able dict, which allows access and
    assignment via object properties rather than dict indexing.
    """

    def __init__(self, *args, **kwargs):
        # we could just call super(DotDict, self).__init__(*args, **kwargs)
        # but that won't get us nested dotdict objects
        od = dict(*args, **kwargs)
        for key, val in od.items():
            if isinstance(val, Mapping):
                value = DotDict(val)
            else:
                value = val
            self[key] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError as ex:
            raise AttributeError("No attribute called: %s" % name) from ex

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError as ex:
            raise AttributeError("No attribute called: %s" % k) from ex

    __setattr__ = dict.__setitem__


def increment_filename_version(path: Path, separator=" ") -> Path:
    stem = path.stem
    try:
        # try to find any existing counter
        splitstem = stem.split(separator)  # raises ValueError on missing sep
        if len(splitstem) < 2:
            raise ValueError()
        counter = int(splitstem[-1])
        stem = separator.join(splitstem[:-1])
    except (ValueError, IndexError):
        # not found, we start with 1
        counter = 1
    return path.with_name(
        "{stem}{sep}{cnt}{suffix}".format(
            stem=stem, sep=separator, cnt=(counter + 1), suffix=path.suffix
        )
    )


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


def dict_merge(dct, merge_dct, add_keys=True):
    """ Recursive dict merge.

    Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    This version will return a copy of the dictionary and leave the original
    arguments untouched.

    The optional argument ``add_keys``, determines whether keys which are
    present in ``merge_dict`` but not ``dct`` should be included in the
    new dict.

    Args:
        dct (dict) onto which the merge is executed
        merge_dct (dict): dct merged into dct
        add_keys (bool): whether to add new keys

    Returns:
        dict: updated dict

    Taken from comment thread: https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    """
    dct = deepcopy(dct)
    if not add_keys:
        merge_dct = {k: merge_dct[k] for k in set(dct).intersection(set(merge_dct))}

    for k, v in merge_dct.items():
        if isinstance(dct.get(k), dict) and isinstance(v, Mapping):
            dct[k] = dict_merge(dct[k], v, add_keys=add_keys)
        else:
            dct[k] = v

    return dct
