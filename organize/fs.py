import time
from pydantic import Field
from pydantic.dataclasses import dataclass
from fs.walk import Walker as FSWalke
from typing import Literal, Set
from pathlib import Path
import os
from fnmatch import fnmatch


def pattern_match(name, patterns):
    # TODO: This can be more performant
    return any(fnmatch(name, pat) for pat in patterns)


@dataclass(frozen=True)
class Walker:
    min_depth: int = 0
    max_depth: int | None = None
    method: Literal["breadth", "depth"] = "breadth"
    filter_dirs: Set[str] | None = None
    filter_files: Set[str] | None = None
    exclude_dirs: Set[str] = Field(default_factory=set)
    exclude_files: Set[str] = Field(default_factory=set)

    def _walk_breadth(self, dir: Path):
        stack = [(dir, 0)]
        while stack:
            cur, lvl = stack.pop()
            try:
                for entry in os.scandir(cur):
                    try:
                        # we do not handle symlinks at the moment
                        if entry.is_symlink():
                            continue
                        if (
                            entry.is_file()
                            and lvl >= self.min_depth
                            and not pattern_match(entry.name, self.exclude_files)
                            and (
                                self.filter_files is None
                                or pattern_match(entry.name, self.filter_files)
                            )
                        ):
                            yield entry
                        elif (
                            entry.is_dir()
                            and not pattern_match(entry.name, self.exclude_dirs)
                            and (
                                self.filter_dirs is None
                                or pattern_match(entry.name, self.filter_dirs)
                            )
                            and not entry.is_symlink()
                        ):
                            if self.max_depth is None or lvl < self.max_depth:
                                stack.append((entry.path, lvl + 1))
                            if lvl >= self.min_depth:
                                yield entry
                    except OSError:
                        pass
            except OSError:
                pass

    def _walk(self, dir: Path):
        if self.method == "breadth":
            yield from self._walk_breadth(dir)
        else:
            raise NotImplemented()

    def files(self, dir: Path):
        for entry in self._walk(dir):
            if entry.is_file():
                yield entry.path

    def dirs(self, dir: Path):
        for entry in self._walk(dir):
            if entry.is_dir():
                yield entry.path


for x in Walker(
    min_depth=0,
    max_depth=2,
    exclude_dirs=(".*", "__pycache__"),
    exclude_files=(".*yml",),
).files(os.path.expanduser("~")):
    print(x)
    time.sleep(0.01)
