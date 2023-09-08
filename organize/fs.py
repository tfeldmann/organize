import time
from pydantic import Field
from pydantic.dataclasses import dataclass
from fs.walk import Walker as FSWalke
from typing import Literal, Set
from pathlib import Path
import os


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
            for entry in os.scandir(cur):
                if (
                    entry.is_file()
                    and lvl >= self.min_depth
                    and entry.name not in self.exclude_files
                    and (self.filter_files is None or entry.name in self.filter_files)
                ):
                    yield entry
                elif (
                    entry.is_dir()
                    and entry.name not in self.exclude_dirs
                    and (self.filter_dirs is None or entry.name in self.filter_dirs)
                    and not entry.is_symlink()
                ):
                    if self.max_depth is None or lvl < self.max_depth:
                        stack.append((entry.path, lvl + 1))
                    if lvl >= self.min_depth:
                        yield entry

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
    exclude_dirs=(
        ".vscode",
        ".git",
        ".ruff_cache",
        ".github",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        "__pycache__",
    ),
).files("."):
    print(x)
    time.sleep(0.01)
