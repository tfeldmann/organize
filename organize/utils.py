import os
import re
import sys
from collections import OrderedDict

import colorama

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


def bold(text):
    # inspired by a feature request from the clint library
    # https://github.com/kennethreitz/clint/issues/157
    if sys.stdout.isatty():
        return "".join([colorama.Style.BRIGHT, str(text), colorama.Style.NORMAL])
    return text


def flatten(arr):
    if arr == []:
        return []
    if not isinstance(arr, list):
        return [arr]
    return flatten(arr[0]) + flatten(arr[1:])


def first_key(dic: dict):
    return list(dic.keys())[0]


class DotDict(OrderedDict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        if not key.startswith("_OrderedDict__"):
            self[key] = value
        else:
            OrderedDict.__setattr__(self, key, value)

    def __delattr__(self, key):
        try:
            self.pop(key)
        except KeyError:
            OrderedDict.__delattr__(self, key)

    def __eq__(self, other):
        return dict.__eq__(self, other)

    def __str__(self):
        return "{%s}" % ", ".join("%r: %r" % (key, self[key]) for key in self)


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
