import fnmatch
import os
import shutil
import unicodedata
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Union

from rich.markup import escape as rich_escape

ENV_ORGANIZE_NORMALIZE_UNICODE = os.environ.get("ORGANIZE_NORMALIZE_UNICODE", "1")


def escape(msg: Any) -> str:
    return rich_escape(str(msg))


def normalize_unicode(
    text: str,
    form: Literal["NFC", "NFD", "NFKC", "NFKD"] = "NFC",
) -> str:
    if ENV_ORGANIZE_NORMALIZE_UNICODE == "1":
        return unicodedata.normalize(form, text)
    return text


@dataclass
class ReportSummary:
    success: int = 0
    errors: int = 0

    def __add__(self, other: "ReportSummary") -> "ReportSummary":
        return ReportSummary(
            success=self.success + other.success,
            errors=self.errors + other.errors,
        )


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


def has_executable(name: str) -> bool:
    return shutil.which(name) is not None


def expandvars(path: Union[str, Path]) -> Path:
    return Path(os.path.expandvars(path)).expanduser()


def glob_match(pattern: str, string: str, *, case_sensitive: bool = False) -> bool:
    if case_sensitive:
        return fnmatch.fnmatchcase(string, pattern)
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
