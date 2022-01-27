"""
Duplicate detection filter.

Based on this stackoverflow answer:
    https://stackoverflow.com/a/36113168/300783

Which I updated for python3 in:
    https://gist.github.com/tfeldmann/fc875e6630d11f2256e746f67a09c1ae
"""
import hashlib
from collections import defaultdict
from fs.base import FS
from typing import Dict, Set, Union, NamedTuple
from organize.output import console

from .filter import Filter

HASH_ALGORITHM = "sha1"


class File(NamedTuple):
    fs: FS
    path: str


def getsize(f: File):
    return f.fs.getsize(f.path)


def full_hash(f: File):
    return f.fs.hash(f.path, name=HASH_ALGORITHM)


def first_chunk_hash(f: File):
    hash_object = hashlib.new(HASH_ALGORITHM)
    with f.fs.openbin(f.path) as file_:
        hash_object.update(file_.read(1024))
    return hash_object.hexdigest()


ORDER_BY = ("location", "created", "lastmodified", "name")


class Duplicate(Filter):
    """
    Finds duplicate files.

    This filter compares files byte by byte and finds identical files with potentially
    different filenames.

    :returns:
        - ``{duplicate}`` -- path to the duplicate source
    """

    name = "duplicate"
    schema_support_instance_without_args = True

    def __init__(self, order_by="location") -> None:
        self.files_for_size = defaultdict(list)
        self.files_for_size  # type: DDict[int, List[PyFSFile]]

        self.files_for_chunk = defaultdict(list)
        self.files_for_chunk  # type: Dict[str, List[PyFSFile]]

        self.file_for_hash = dict()
        self.file_for_hash  # type: Dict[str, PyFSFile]

        # we keep track of the files we already computed the hashes for so we only do
        # that once.
        self.first_chunk_known = set()  # type: Set[PyFSFile]
        self.hash_known = set()  # type: Set[PyFSFile]

    def matches(self, fs: FS, path: str) -> Union[bool, Dict[str, str]]:
        file_ = File(fs=fs, path=path)
        # the exact same path has already been handled. This happens if multiple
        # locations emit this file in a single rule. We skip these.
        if file_ in self.first_chunk_known:
            return False

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
        original = self.file_for_hash.get(hash_)
        if original:
            return {"duplicate": original}

        return False

    def pipeline(self, args):
        fs = args["fs"]
        fs_path = args["fs_path"]
        if fs.isdir(fs_path):
            raise EnvironmentError("Dirs are not supported")
        try:
            return self.matches(fs=fs, path=fs_path)
        except Exception:
            console.print_exception()

    def __str__(self) -> str:
        return "Duplicate()"
