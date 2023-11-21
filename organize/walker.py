import os
from fnmatch import fnmatch
from typing import Generator, Iterable, Iterator, List, Literal, NamedTuple, Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


def pattern_match(name, patterns):
    # TODO: This can be more performant!
    return any(fnmatch(name, pat) for pat in patterns)


class ScandirResult(NamedTuple):
    dirs: List[os.DirEntry]
    nondirs: List[os.DirEntry]


def scandir(top: str, collectfiles: bool = True):
    result = ScandirResult([], [])
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
    return result


@dataclass(frozen=True)
class Walker:
    min_depth: int = 0
    max_depth: Optional[int] = None
    method: Literal["breadth", "depth"] = "breadth"
    filter_dirs: Optional[Iterable[str]] = None
    filter_files: Optional[Iterable[str]] = None
    exclude_dirs: Iterable[str] = Field(default_factory=set)
    exclude_files: Iterable[str] = Field(default_factory=set)

    def _should_yield_file(self, entry: os.DirEntry, lvl: int):
        return (
            lvl >= self.min_depth
            and not pattern_match(entry.name, self.exclude_files)
            and (
                self.filter_files is None
                or pattern_match(entry.name, self.filter_files)
            )
        )

    def _dirs_list_yield_walk(self, entries: Iterable[os.DirEntry], lvl: int):
        to_yield, to_walk = [], []
        for entry in entries:
            if not pattern_match(entry.name, self.exclude_dirs) and (
                self.filter_dirs is None or pattern_match(entry.name, self.filter_dirs)
            ):
                if self.max_depth is None or lvl < self.max_depth:
                    to_walk.append(entry)
                if lvl >= self.min_depth:
                    to_yield.append(entry)
        return (to_yield, to_walk)

    def walk(self, top: str, files: bool = True, dirs: bool = True, lvl: int = 0):
        if not files and not dirs:
            return

        # list all dirs and nondirs of the folder
        result = scandir(top, collectfiles=files)

        if self.method == "breadth":
            # Return entries
            for entry in result.nondirs:
                if files and self._should_yield_file(entry=entry, lvl=lvl):
                    yield entry
            to_yield, to_walk = self._dirs_list_yield_walk(result.dirs, lvl=lvl)
            if dirs:
                yield from to_yield
            # Recurse into sub-directories
            for entry in to_walk:
                yield from self.walk(entry.path, files=files, dirs=dirs, lvl=lvl + 1)

        elif self.method == "depth":
            to_yield, to_walk = self._dirs_list_yield_walk(result.dirs, lvl=lvl)
            # Recurse into sub-directories
            for entry in to_walk:
                yield from self.walk(entry.path, files=files, dirs=dirs, lvl=lvl + 1)
            # Return entries
            for entry in result.nondirs:
                if files and self._should_yield_file(entry=entry, lvl=lvl):
                    yield entry
            if dirs:
                yield from to_yield
        else:
            raise ValueError(f'Unknown method "{self.method}"')

    def files(self, dir: str) -> Iterator[str]:
        for entry in self.walk(dir, files=True, dirs=False):
            yield entry.path

    def dirs(self, dir: str) -> Iterator[str]:
        for entry in self.walk(dir, files=False, dirs=True):
            yield entry.path
