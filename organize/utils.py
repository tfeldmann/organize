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

unescaped_wildcard = re.compile(r'(?<!\\)[\*\?\[]+')


def splitglob(globstr):
    """ split a string with wildcards into a base folder and globstring """
    path = fullpath(globstr.strip())
    parts = path.parts
    for i, part in enumerate(parts):
        if unescaped_wildcard.search(part):
            return (Path(*parts[:i]), str(Path(*parts[i:])))
    return (path, '')


def fullpath(path):
    """ Expand '~' and resolve the given path """
    return Path(path).expanduser().resolve(strict=False)


def bold(text):
    # inspired by a feature request from the clint library
    # https://github.com/kennethreitz/clint/issues/157
    if sys.stdout.isatty():
        return ''.join([colorama.Style.BRIGHT, str(text), colorama.Style.NORMAL])
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
        if not key.startswith('_OrderedDict__'):
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
        return '{%s}' % ', '.join('%r: %r' % (key, self[key]) for key in self)


def find_unused_filename(path: Path) -> Path:
    """
    we assume path already exists. This function then adds a counter to the
    filename until we find a unused filename.
    """
    stem = path.stem
    try:
        splitstem = stem.split(' ')
        if len(splitstem) < 2:
            raise ValueError()
        count = int(splitstem[-1])
        stem = ' '.join(splitstem[:-1])
    except (ValueError, IndexError):
        count = 1
    while True:
        count += 1
        tmp_path = path.with_name('%s %s%s' % (stem, count, path.suffix))
        if not tmp_path.exists():
            return tmp_path
