# https://stackoverflow.com/a/36113168/300783
import hashlib
import os
from collections import defaultdict
from typing import DefaultDict as DDict
from typing import Dict, List, Optional, Set, Union

from organize.utils import fullpath

from .filter import Filter


def chunk_reader(fobj, chunk_size=1024):
    """ Generator that reads a file in chunks of bytes """
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


def get_hash(filename, first_chunk_only=False, hash_algo=hashlib.sha1):
    hashobj = hash_algo()
    with open(filename, "rb") as f:
        if first_chunk_only:
            hashobj.update(f.read(1024))
        else:
            for chunk in chunk_reader(f):
                hashobj.update(chunk)
    return hashobj.digest()


class Duplicate(Filter):
    def __init__(self) -> None:
        self.files_by_size = defaultdict(list)  # type: DDict[int, List[str]]
        self.files_by_small_hash = defaultdict(list)  # type: DDict[bytes, List[str]]
        self.files_by_full_hash = dict()  # type: Dict[bytes, str]

        # we keep track of which files we already computed the hashes for so we only do
        # that once.
        self.small_hash_known = set()  # type: Set[str]

    def register_small_hash(self, path: str) -> Optional[bytes]:
        if path not in self.small_hash_known:
            small_hash = get_hash(path, first_chunk_only=True)
            self.files_by_small_hash[small_hash].append(path)
            self.small_hash_known.add(path)
            return small_hash
        return None  # already registered

    def register_full_hash(self, path: str) -> Optional[str]:
        full_hash = get_hash(path, first_chunk_only=False)
        duplicate = self.files_by_full_hash.get(full_hash)
        if duplicate:
            return duplicate
        self.files_by_full_hash[full_hash] = path
        return None

    def matches(self, path: str) -> Union[bool, Dict[str, str]]:
        # Check for files with similar size
        file_size = os.path.getsize(path)
        same_size = self.files_by_size[file_size]
        candidates_fsize = same_size[:]
        same_size.append(path)
        if not candidates_fsize:
            # the file is unique in size and cannot be a duplicate
            return False

        # For all other files with the same file size, get their hash of the first 1024
        # bytes
        for candidate in candidates_fsize:
            self.register_small_hash(candidate)
        small_hash = self.register_small_hash(path)
        if not small_hash:
            # the file has already been handled.
            return False

        candidates_small = self.files_by_small_hash[small_hash][:-1]
        for candidate in candidates_small:
            dup = self.register_full_hash(candidate)
            # assert not dup, "full hash of %s already registered" % dup
        duplicate = self.register_full_hash(path)
        if duplicate:
            return {"duplicate": duplicate}
        return False

    def pipeline(self, args):
        return self.matches(str(fullpath(args["path"])))

    def __str__(self) -> str:
        return "Duplicate()"
