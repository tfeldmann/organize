import fnmatch
import os
from copy import deepcopy
from pathlib import Path
from typing import Any, Union


class ChangeDetector:
    def __init__(self):
        self._prev = None
        self._ready = False

    def changed(self, value: Any) -> bool:
        if not self._ready:
            self._prev = value
            self._ready = True
            return True
        else:
            changed = value != self._prev
            self._prev = value
            return changed

    def reset(self) -> None:
        self._ready = False


def expandvars(path: Union[str, Path]) -> Path:
    return Path(os.path.expandvars(path)).expanduser()


def glob_match(pattern: str, string: str, *, case_sensitive: bool = False):
    if case_sensitive:
        return fnmatch.fnmatchcase(string, pattern)
    else:
        return fnmatch.fnmatch(string.lower(), pattern.lower())


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
