"""
Duplicate detection filter.

Based on this stackoverflow answer:
    https://stackoverflow.com/a/36113168/300783

Which I updated for python3 in:
    https://gist.github.com/tfeldmann/fc875e6630d11f2256e746f67a09c1ae
"""
import hashlib
from collections import defaultdict
from typing import Dict, NamedTuple, Set, Union

from fs.base import FS
from fs.path import basename

from organize.utils import is_same_resource

from .filter import Filter, FilterResult

HASH_ALGORITHM = "sha1"
DETECTION_METHODS = ("first_seen", "name", "created", "lastmodified")
DETECTION_METHOD_REGEX = r"(-?)\s*?({})".format("|".join(DETECTION_METHODS))


class File(NamedTuple):
    fs: FS
    path: str
    base_path: str

    @property
    def lastmodified(self):
        return self.fs.getmodified(self.path)

    @property
    def created(self):
        return self.fs.getinfo(self.path, namespaces=["details"]).created

    @property
    def name(self):
        return basename(self.path)


def getsize(f: File):
    return f.fs.getsize(f.path)


def full_hash(f: File):
    return f.fs.hash(f.path, name=HASH_ALGORITHM)


def first_chunk_hash(f: File):
    hash_object = hashlib.new(HASH_ALGORITHM)
    with f.fs.openbin(f.path) as file_:
        hash_object.update(file_.read(1024))
    return hash_object.hexdigest()


def detect_original(known: File, new: File, method: str, reverse: bool):
    """Returns a tuple (original file, duplicate)"""

    if method == "first_seen":
        return (known, new) if not reverse else (new, known)
    elif method == "name":
        return tuple(sorted((known, new), key=lambda x: x.name, reverse=reverse))
    elif method == "created":
        return tuple(sorted((known, new), key=lambda x: x.created, reverse=reverse))
    elif method == "lastmodified":
        return tuple(
            sorted((known, new), key=lambda x: x.lastmodified, reverse=reverse)
        )
    else:
        raise ValueError("Unknown original detection method: %s" % method)


class Duplicate(Filter):
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
            - `"lastmodified"`: The first file sorted by date of last modification is the original.

    You can reverse the sorting method by prefixing a `-`.

    So with `detect_original_by: "-created"` the file with the older creation date is
    the original and the younger file is the duplicate. This works on all methods, for
    example `"-first_seen"`, `"-name"`, `"-created"`, `"-lastmodified"`.

    **Returns:**

    `{duplicate.original}` - The path to the original
    """

    name = "duplicate"
    schema_support_instance_without_args = True

    def __init__(self, detect_original_by="first_seen"):
        if detect_original_by.startswith("-"):
            self.detect_original_by = detect_original_by[1:]
            self.select_orignal_reverse = True
        else:
            self.detect_original_by = detect_original_by
            self.select_orignal_reverse = False

        self.files_for_size = defaultdict(list)
        self.files_for_chunk = defaultdict(list)
        self.file_for_hash = dict()

        # we keep track of the files we already computed the hashes for so we only do
        # that once.
        self.seen_files = set()  # type: Set[File]
        self.first_chunk_known = set()  # type: Set[File]
        self.hash_known = set()  # type: Set[File]

    def matches(self, fs: FS, path: str, base_path: str):
        file_ = File(fs=fs, path=path, base_path=base_path)
        # the exact same path has already been handled. This happens if multiple
        # locations emit this file in a single rule or if we follow symlinks.
        # We skip these.
        if file_ in self.seen_files or any(
            is_same_resource(file_.fs, file_.path, x.fs, x.path)
            for x in self.seen_files
        ):
            return False

        self.seen_files.add(file_)

        # check for files with equal size
        file_size = getsize(file_)
        same_size = self.files_for_size[file_size]
        same_size.append(file_)
        if len(same_size) == 1:
            # the file is unique in size and cannot be a duplicate
            return False

        # for all other files with the same file size:
        # make sure we know their hash of their first 1024 byte chunk
        for f in same_size[:-1]:
            if f not in self.first_chunk_known:
                chunk_hash = first_chunk_hash(f)
                self.first_chunk_known.add(f)
                self.files_for_chunk[chunk_hash].append(f)

        # check first chunk hash collisions with the current file
        chunk_hash = first_chunk_hash(file_)
        same_first_chunk = self.files_for_chunk[chunk_hash]
        same_first_chunk.append(file_)
        self.first_chunk_known.add(file_)
        if len(same_first_chunk) == 1:
            # the file has a unique small hash and cannot be a duplicate
            return False

        # Ensure we know the full hashes of all files with the same first chunk as
        # the investigated file
        for f in same_first_chunk[:-1]:
            if f not in self.hash_known:
                hash_ = full_hash(f)
                self.hash_known.add(f)
                self.file_for_hash[hash_] = f

        # check full hash collisions with the current file
        hash_ = full_hash(file_)
        self.hash_known.add(file_)
        known = self.file_for_hash.get(hash_)
        if known:
            original, duplicate = detect_original(
                known=known,
                new=file_,
                method=self.detect_original_by,
                reverse=self.select_orignal_reverse,
            )
            if known != original:
                self.file_for_hash[hash_] = original

            resource_changed_reason = "duplicate of" if known != original else None
            from organize.core import syspath_or_exception

            return {
                "fs": duplicate.fs,
                "fs_path": duplicate.path,
                "fs_base_path": duplicate.base_path,
                "resource_changed": resource_changed_reason,
                self.get_name(): {
                    "original": syspath_or_exception(original.fs, original.path)
                },
            }

        return False

    def pipeline(self, args):
        fs = args["fs"]
        fs_path = args["fs_path"]
        fs_base_path = args["fs_base_path"]
        if fs.isdir(fs_path):
            raise EnvironmentError("Dirs are not supported")
        result = self.matches(fs=fs, path=fs_path, base_path=fs_base_path)
        if result is False:
            return FilterResult(matches=False, updates={})
        return FilterResult(matches=True, updates=result)

    def __str__(self) -> str:
        return "Duplicate()"
