"""
This file is based on fs.glob.

Unused stuff is removed and arguments are added which are provided to the internal
walker object.
"""

from __future__ import unicode_literals

from collections import namedtuple
import re
import typing

from fs.lrucache import LRUCache
from fs._repr import make_repr
from fs.path import iteratepath
from fs import wildcard


GlobMatch = namedtuple("GlobMatch", ["path", "info"])

if typing.TYPE_CHECKING:
    from typing import Iterator, List, Optional, Pattern, Text, Tuple
    from fs.base import FS


_PATTERN_CACHE = LRUCache(
    1000
)  # type: LRUCache[Tuple[Text, bool], Tuple[int, bool, Pattern]]


def _translate_glob(pattern, case_sensitive=True):
    levels = 0
    recursive = False
    re_patterns = [""]
    for component in iteratepath(pattern):
        if component == "**":
            re_patterns.append(".*/?")
            recursive = True
        else:
            re_patterns.append(
                "/" + wildcard._translate(component, case_sensitive=case_sensitive)
            )
        levels += 1
    re_glob = "(?ms)^" + "".join(re_patterns) + ("/$" if pattern.endswith("/") else "$")
    return (
        levels,
        recursive,
        re.compile(re_glob, 0 if case_sensitive else re.IGNORECASE),
    )


def match(pattern, path):
    # type: (str, str) -> bool
    """Compare a glob pattern with a path (case sensitive).

    Arguments:
        pattern (str): A glob pattern.
        path (str): A path.

    Returns:
        bool: ``True`` if the path matches the pattern.

    Example:

        >>> from fs.glob import match
        >>> match("**/*.py", "/fs/glob.py")
        True

    """
    try:
        levels, recursive, re_pattern = _PATTERN_CACHE[(pattern, True)]
    except KeyError:
        levels, recursive, re_pattern = _translate_glob(pattern, case_sensitive=True)
        _PATTERN_CACHE[(pattern, True)] = (levels, recursive, re_pattern)
    return bool(re_pattern.match(path))


def imatch(pattern, path):
    # type: (str, str) -> bool
    """Compare a glob pattern with a path (case insensitive).

    Arguments:
        pattern (str): A glob pattern.
        path (str): A path.

    Returns:
        bool: ``True`` if the path matches the pattern.

    """
    try:
        levels, recursive, re_pattern = _PATTERN_CACHE[(pattern, False)]
    except KeyError:
        levels, recursive, re_pattern = _translate_glob(pattern, case_sensitive=True)
        _PATTERN_CACHE[(pattern, False)] = (levels, recursive, re_pattern)
    return bool(re_pattern.match(path))


class Globber(object):
    """A generator of glob results.

        Arguments:
            fs (~fs.base.FS): A filesystem object
            pattern (str): A glob pattern, e.g. ``"**/*.py"``
            path (str): A path to a directory in the filesystem.
            namespaces (list): A list of additional info namespaces.
            case_sensitive (bool): If ``True``, the path matching will be
                case *sensitive* i.e. ``"FOO.py"`` and ``"foo.py"`` will
                be different, otherwise path matching will be case *insensitive*.
            exclude_dirs (list): A list of patterns to exclude when searching,
                e.g. ``["*.git"]``.

    """

    def __init__(
        self,
        fs,
        pattern,
        path="/",
        namespaces=None,
        case_sensitive=True,
        exclude_dirs=None,
        max_depth=None,
        exclude_files=None,
        search="breadth",
        ignore_errors=False,
    ):
        # type: (FS, str, str, Optional[List[str]], bool, Optional[List[str]]) -> None
        self.fs = fs
        self.pattern = pattern
        self.path = path
        self.namespaces = namespaces
        self.case_sensitive = case_sensitive
        self.exclude_dirs = exclude_dirs

        # added parameters
        self.max_depth = max_depth
        self.exclude_files = exclude_files
        self.search = search
        self.ignore_errors = ignore_errors

    def __repr__(self):
        return make_repr(
            self.__class__.__name__,
            self.fs,
            self.pattern,
            path=(self.path, "/"),
            namespaces=(self.namespaces, None),
            case_sensitive=(self.case_sensitive, True),
            exclude_dirs=(self.exclude_dirs, None),
            max_depth=(self.max_depth, None),
            exclude_files=(self.exclude_files, None),
            search=(self.search, "breadth"),
            ignore_errors=(self.ignore_errors, False),
        )

    def _make_iter(self, namespaces=None):
        # type: (str, List[str]) -> Iterator[GlobMatch]
        try:
            levels, recursive, re_pattern = _PATTERN_CACHE[
                (self.pattern, self.case_sensitive)
            ]
        except KeyError:
            levels, recursive, re_pattern = _translate_glob(
                self.pattern, case_sensitive=self.case_sensitive
            )

        max_depth = None if recursive else levels
        if self.max_depth is not None:
            if max_depth is None:
                max_depth = self.max_depth
            else:
                max_depth = min(max_depth, self.max_depth)

        for path, info in self.fs.walk.info(
            path=self.path,
            namespaces=namespaces or self.namespaces,
            max_depth=max_depth,
            exclude_dirs=self.exclude_dirs,
            exclude=self.exclude_files,
            search=self.search,
            ignore_errors=self.ignore_errors,
        ):
            if info.is_dir:
                path += "/"
            if re_pattern.match(path):
                yield GlobMatch(path, info)

    def __iter__(self):
        # type: () -> Iterator[GlobMatch]
        """An iterator of :class:`fs.glob.GlobMatch` objects."""
        return self._make_iter()
