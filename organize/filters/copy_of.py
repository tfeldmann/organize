from collections import defaultdict
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Set

from pydantic import Field
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.duplicates import original_of, walk_files
from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import render
from organize.validators import FlatList

from .hash import hash


@dataclass(config=ConfigDict(extra="forbid"))
class CopyOf:
    """Matches files whose content is identical to a file that already exists,
    no matter what the files are called.

    By default the whole location is searched, including all its subfolders, so a
    new download is recognized as a copy of a file you sorted before. Of several
    identical new files the first one is the original.

    Attributes:
        search (list(str)):
            Additional folders to search for originals (including their
            subfolders), e.g. `~/Documents`.

    **Returns:**

    - `{copy_of.original}`: The path to the existing file
    """

    search: FlatList[str] = Field(default_factory=list)

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="copy_of",
        files=True,
        dirs=False,
    )

    def __post_init__(self):
        # files by size, so only files of the same size are hashed
        self._by_size: Dict[int, List[Path]] = defaultdict(list)
        self._hashes: Dict[Path, str] = {}
        self._indexed: Set[Path] = set()

    def _index(self, folder: Path, skip_top_level: Optional[Path] = None) -> None:
        folder = folder.resolve()
        if folder in self._indexed or not folder.is_dir():
            return
        self._indexed.add(folder)
        for path in walk_files(folder):
            # unsorted files in the location are compared in the order they are seen
            if skip_top_level is not None and path.parent == skip_top_level:
                continue
            self._add(path)

    def _add(self, path: Path) -> None:
        try:
            self._by_size[path.stat().st_size].append(path)
        except OSError:
            pass

    def _hash(self, path: Path) -> str:
        if path not in self._hashes:
            self._hashes[path] = hash(path, algo="sha256")
        return self._hashes[path]

    def find_original(self, path: Path) -> Optional[Path]:
        size = path.stat().st_size
        if size == 0:
            return None  # empty files are all alike
        fallback = None
        for candidate in self._by_size.get(size, []):
            if candidate == path or not candidate.exists():
                continue
            if self._hash(candidate) != self._hash(path):
                continue
            if original_of(candidate) is None:
                return candidate
            # rather point to the original than to another copy
            fallback = fallback or candidate
        return fallback

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None, "Does not support standalone mode"
        path = res.path.resolve()
        if res.basedir is not None:
            basedir = res.basedir.resolve()
            self._index(basedir, skip_top_level=basedir)
        for folder in self.search:
            self._index(Path(render(folder)))

        original = self.find_original(path)
        if original is None:
            self._add(path)  # the first of several new copies is the original
            return False
        res.vars[self.filter_config.name] = {"original": original}
        return True
