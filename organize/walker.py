import os
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, Iterator, List, Literal, NamedTuple, Optional, Set

from natsort import os_sorted
from pydantic import Field
from pydantic.dataclasses import dataclass


def pattern_match(name: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch(name, pat) for pat in patterns)


class ScandirResult(NamedTuple):
    dirs: List[os.DirEntry]
    nondirs: List[os.DirEntry]


def scandir(top: str, collectfiles: bool = True) -> ScandirResult:
    result = ScandirResult(dirs=[], nondirs=[])
    try:
        # build iterator if we have the permissions to this folder
        scandir_it = os.scandir(top)
    except OSError:
        return result

    with scandir_it:
        while True:
            try:
                try:
                    entry = next(scandir_it)
                except StopIteration:
                    break
            except OSError:
                return result

            try:
                is_symlink = entry.is_symlink()
            except OSError:
                # If is_symlink() raises an OSError, consider that the
                # entry is not a symbolic link, same behaviour than
                # os.path.islink().
                is_symlink = False

            # As of now, we skip all symlinks.
            if is_symlink:
                continue

            try:
                is_dir = entry.is_dir()
            except OSError:
                # If is_dir() raises an OSError, consider that the entry is not
                # a directory, same behaviour than os.path.isdir().
                is_dir = False

            if is_dir:
                result.dirs.append(entry)
            elif collectfiles:
                result.nondirs.append(entry)
    return ScandirResult(
        dirs=os_sorted(result.dirs, key=lambda x: x.name),
        nondirs=os_sorted(result.nondirs, key=lambda x: x.name),
    )


class DirMatchResult(NamedTuple):
    """What to do with the matched dir."""

    should_walk_into: bool
    should_yield: bool

    def __bool__(self) -> bool:
        return self.should_walk_into or self.should_yield


class Queue(NamedTuple):
    to_yield: List[os.DirEntry]
    to_walk: List[os.DirEntry]


@dataclass(frozen=True)
class Walker:
    min_depth: int = 0
    max_depth: Optional[int] = None
    method: Literal["breadth", "depth"] = "breadth"
    filter_dirs: Optional[List[str]] = None
    filter_files: Optional[List[str]] = None
    exclude_dirs: Set[str] = Field(default_factory=set)
    exclude_files: Set[str] = Field(default_factory=set)

    def _file_match(self, filename: str, lvl: int) -> bool:
        return (
            lvl >= self.min_depth
            and not pattern_match(filename, self.exclude_files)
            and (
                self.filter_files is None or pattern_match(filename, self.filter_files)
            )
        )

    def _dir_match(self, dirname: str, lvl: int) -> DirMatchResult:
        should_walk, should_yield = False, False
        if not pattern_match(dirname, self.exclude_dirs) and (
            self.filter_dirs is None or pattern_match(dirname, self.filter_dirs)
        ):
            if self.max_depth is None or lvl < self.max_depth:
                should_walk = True
            if lvl >= self.min_depth:
                should_yield = True
        return DirMatchResult(
            should_walk_into=should_walk,
            should_yield=should_yield,
        )

    def _queue_dirs(self, entries: Iterable[os.DirEntry], lvl: int) -> Queue:
        result = Queue(to_yield=[], to_walk=[])
        for entry in entries:
            actions = self._dir_match(dirname=entry.name, lvl=lvl)
            if actions.should_walk_into:
                result.to_walk.append(entry)
            if actions.should_yield:
                result.to_yield.append(entry)
        return result

    def walk(
        self,
        top: str,
        files: bool = True,
        dirs: bool = True,
        lvl: int = 0,
    ) -> Iterator[os.DirEntry]:
        if not files and not dirs:
            return

        # list all dirs and nondirs of the folder
        result = scandir(top, collectfiles=files)

        if self.method == "breadth":
            # Breadth-first: First return entries from the current dir
            for entry in result.nondirs:
                if files and self._file_match(filename=entry.name, lvl=lvl):
                    yield entry
            queue = self._queue_dirs(result.dirs, lvl=lvl)
            if dirs:
                yield from queue.to_yield
            # then recurse into sub-directories
            for entry in queue.to_walk:
                yield from self.walk(entry.path, files=files, dirs=dirs, lvl=lvl + 1)

        elif self.method == "depth":
            # Depth-first: First recurse into sub-directories
            queue = self._queue_dirs(result.dirs, lvl=lvl)
            for entry in queue.to_walk:
                yield from self.walk(entry.path, files=files, dirs=dirs, lvl=lvl + 1)
            # then return entries
            for entry in result.nondirs:
                if files and self._file_match(filename=entry.name, lvl=lvl):
                    yield entry
            if dirs:
                yield from queue.to_yield
        else:
            raise ValueError(f'Unknown method "{self.method}"')

    def files(self, path: str) -> Iterator[Path]:
        # if path is a single file we emit just the path itself
        if os.path.isfile(path):
            yield Path(path)
            return
        # otherwise we walk the given folder
        for entry in self.walk(path, files=True, dirs=False):
            yield Path(entry.path)

    def dirs(self, path: str) -> Iterator[Path]:
        for entry in self.walk(path, files=False, dirs=True):
            yield Path(entry.path)

    def would_emit(self, walkdir: Path, path: Path) -> bool:
        # for every part of the relative path, check if we have file or dir actions.
        if not path.is_relative_to(walkdir):
            return False
        return True
