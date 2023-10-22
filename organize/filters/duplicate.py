"""
Duplicate detection filter.

Based on this stackoverflow answer:
    https://stackoverflow.com/a/36113168/300783

Which was updated for python3 in:
    https://gist.github.com/tfeldmann/fc875e6630d11f2256e746f67a09c1ae
"""
from collections import defaultdict
from pathlib import Path
from typing import ClassVar, Literal, Tuple

from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.filters.created import read_created
from organize.filters.hash import hash, hash_first_chunk
from organize.filters.lastmodified import read_lastmodified
from organize.filters.size import read_file_size
from organize.output import Output
from organize.resource import Resource

DetectionMethod = Literal[
    "first_seen",
    "-first_seen",
    "name",
    "-name",
    "created",
    "-created",
    "lastmodified",
    "-lastmodified",
]


def detect_original(
    known: Path, new: Path, method: DetectionMethod, reverse: bool
) -> Tuple[Path, Path]:
    """Returns a tuple (original file, duplicate)"""

    if method == "first_seen":
        return (known, new) if not reverse else (new, known)
    elif method == "name":
        return tuple(
            sorted(
                (known, new),
                key=lambda x: x.name,
                reverse=reverse,
            )
        )
    elif method == "created":
        return tuple(
            sorted(
                (known, new),
                key=lambda x: read_created(x),
                reverse=reverse,
            )
        )
    elif method == "lastmodified":
        return tuple(
            sorted((known, new), key=lambda x: read_lastmodified(x), reverse=reverse)
        )
    else:
        raise ValueError(f"Unknown original detection method: {method}")


@dataclass
class Duplicate:
    """A fast duplicate file finder.

    This filter compares files byte by byte and finds identical files with potentially
    different filenames.

    Args:
        detect_original_by (str):
            Detection method to distinguish between original and duplicate.
            Possible values are:

            - `"first_seen"`: Whatever file is visited first is the original. This
              depends on the order of your location entries.
            - `"name"`: The first entry sorted by name is the original.
            - `"created"`: The first entry sorted by creation date is the original.
            - `"lastmodified"`: The first file sorted by date of last modification is
               the original.

    You can reverse the sorting method by prefixing a `-`.

    So with `detect_original_by: "-created"` the file with the older creation date is
    the original and the younger file is the duplicate. This works on all methods, for
    example `"-first_seen"`, `"-name"`, `"-created"`, `"-lastmodified"`.

    **Returns:**

    `{duplicate.original}` - The path to the original
    """

    detect_original_by: DetectionMethod = "first_seen"
    hash_algorithm: str = "sha1"

    filter_config: ClassVar = FilterConfig(name="duplicate", files=True, dirs=False)

    def __post_init__(self):
        # reverse original detection order if starting with "-"
        self._detect_original_by = self.detect_original_by
        self._detect_original_reverse = False
        if self.detect_original_by.startswith("-"):
            self._detect_original_by = self.detect_original_by[1:]
            self._detect_original_reverse = True

        self._files_for_size = defaultdict(list)
        self._files_for_chunk = defaultdict(list)
        self._file_for_hash = dict()

        # we keep track of the files we already computed the hashes for so we only do
        # that once.
        self._seen_files = set()
        self._first_chunk_known = set()
        self._hash_known = set()

    def pipeline(self, res: Resource, output: Output) -> bool:
        # skip symlinks
        if res.path.is_symlink():
            return False

        # the exact same path has already been handled. This happens if multiple
        # locations emit this file in a single rule or if we follow symlinks.
        # We skip these.
        if res.path in self._seen_files:
            return False

        self._seen_files.add(res.path)

        # check for files with equal size
        file_size = read_file_size(path=res.path)
        same_size = self._files_for_size[file_size]
        same_size.append(res.path)
        if len(same_size) == 1:
            # the file is unique in size and cannot be a duplicate
            return False

        # for all other files with the same file size:
        # make sure we know their hash of their first 1024 byte chunk
        for f in same_size[:-1]:
            if f not in self._first_chunk_known:
                chunk_hash = hash_first_chunk(f, algo=self.hash_algorithm)
                self._first_chunk_known.add(f)
                self._files_for_chunk[chunk_hash].append(f)

        # check first chunk hash collisions with the current file
        chunk_hash = hash_first_chunk(res.path, algo=self.hash_algorithm)
        same_first_chunk = self._files_for_chunk[chunk_hash]
        same_first_chunk.append(res.path)
        self._first_chunk_known.add(res.path)
        if len(same_first_chunk) == 1:
            # the file has a unique small hash and cannot be a duplicate
            return False

        # Ensure we know the full hashes of all files with the same first chunk as
        # the investigated file
        for f in same_first_chunk[:-1]:
            if f not in self._hash_known:
                hash_ = hash(f, algo=self.hash_algorithm)
                self._hash_known.add(f)
                self._file_for_hash[hash_] = f

        # check full hash collisions with the current file
        hash_ = hash(res.path, algo=self.hash_algorithm)
        self._hash_known.add(res.path)
        known = self._file_for_hash.get(hash_)
        if known:
            original, duplicate = detect_original(
                known=known,
                new=res.path,
                method=self._detect_original_by,
                reverse=self._detect_original_reverse,
            )
            if known != original:
                self._file_for_hash[hash_] = original

            resource_changed_reason = "duplicate of" if known != original else None

            res.path = duplicate
            res.vars[self.filter_config.name] = {"original": original}
            return True

        return False
