import os
import re
from collections.abc import Mapping
from copy import deepcopy
from typing import Any, Sequence, Tuple, Union, List, Hashable

from .compat import Path

WILDCARD_REGEX = re.compile(r"(?<!\\)[\*\?\[]+")


def splitglob(globstr: str) -> Tuple[Path, str]:
    """ split a string with wildcards into a base folder and globstring """
    path = fullpath(globstr.strip())
    parts = path.parts
    for i, part in enumerate(parts):
        if WILDCARD_REGEX.search(part):
            return (Path(*parts[:i]), str(Path(*parts[i:])))
    return (path, "")


def fullpath(path: Union[str, Path]) -> Path:
    """ Expand '~' and resolve the given path. Path can be a string or a Path obj. """
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


class DotDict(dict):
    """
    Quick and dirty implementation of a dot-able dict, which allows access and
    assignment via object properties rather than dict indexing.
    Keys are case insensitive.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        # we could just call super(DotDict, self).__init__(*args, **kwargs)
        # but that won't get us nested dotdict objects
        od = dict(*args, **kwargs)
        for key, val in od.items():
            if isinstance(val, Mapping):
                value = DotDict(val)
            else:
                value = val
            self[self.normkey(key)] = value

    @staticmethod
    def normkey(key):
        if isinstance(key, str):
            return key.lower()
        else:
            return key

    def __delattr__(self, key):
        try:
            del self[self.normkey(key)]
        except KeyError as ex:
            raise AttributeError("No attribute called: %s" % key) from ex

    def __getattr__(self, key):
        try:
            return self[self.normkey(key)]
        except KeyError as ex:
            raise AttributeError("No attribute called: %s" % key) from ex

    def __setattr__(self, key, value):
        self[self.normkey(key)] = value

    def update(self, other):
        """ recursively update the dotdict instance with another dicts items """
        for key, val in other.items():
            normkey = self.normkey(key)
            if isinstance(val, Mapping):
                if isinstance(self.get(normkey), dict):
                    self[normkey].update(val)
                else:
                    self[normkey] = __class__(val)
            else:
                self[normkey] = val

    def merge(self, other) -> Mapping:
        """ recursively merge values from another dict and return a new instance """
        new_dct = deepcopy(self)
        new_dct.update(other)
        return new_dct


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
