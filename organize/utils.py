import sys
if sys.version_info < (3, 5):
    from pathlib2 import Path
else:
    from pathlib import Path
from collections import OrderedDict

import colorama


def bold(text):
    # inspired by a feature request from the clint library
    # https://github.com/kennethreitz/clint/issues/157
    if sys.stdout.isatty():
        return ''.join([colorama.Style.BRIGHT, text, colorama.Style.NORMAL])
    else:
        return text


def flatten(arr):
    if arr == []:
        return []
    if not isinstance(arr, list):
        return [arr]
    return flatten(arr[0]) + flatten(arr[1:])


def first_key(d):
    return list(d.keys())[0]


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
