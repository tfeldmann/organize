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

    """
    Example:

        rules:
          - folders:
              - ~/Desktop
              - ~/Downloads
            subfolders: true
            filters:
              - duplicate
            actions:
              - echo: "{path} is a duplicate of {duplicate}"

    """

    def __init__(self) -> None:
        self.files_for_size = defaultdict(list)  # type: DDict[int, List[str]]
        self.files_for_small_hash = defaultdict(list)  # type: DDict[bytes, List[str]]
        self.file_for_full_hash = dict()  # type: Dict[bytes, str]

        # we keep track of which files we already computed the hashes for so we only do
        # that once.
        self.small_hash_known = set()  # type: Set[str]
        self.full_hash_known = set()  # type: Set[str]

    def matches(self, path: str) -> Union[bool, Dict[str, str]]:
        # the exact same path has already been handled. This might happen if path is a
        # symlink which resolves to file that is already known. We skip these.
        if path in self.small_hash_known:
            return False

        # Check for files with equal size
        file_size = os.path.getsize(path)
        same_size = self.files_for_size[file_size]
        candidates_fsize = same_size[:]
        same_size.append(path)
        if not candidates_fsize:
            # the file is unique in size and cannot be a duplicate
            return False

        # For all other files with the same file size, get their hash of the first 1024
        # bytes
        for c in candidates_fsize:
            if c not in self.small_hash_known:
                try:
                    c_small_hash = get_hash(c, first_chunk_only=True)
                    self.files_for_small_hash[c_small_hash].append(c)
                    self.small_hash_known.add(c)
                except OSError:
                    pass

        small_hash = get_hash(path, first_chunk_only=True)
        same_small_hash = self.files_for_small_hash[small_hash]
        candidates_shash = same_small_hash[:]
        same_small_hash.append(path)
        self.small_hash_known.add(path)
        if not candidates_shash:
            # the file has a unique small hash and cannot be a duplicate
            return False

        for c in candidates_shash:
            if c not in self.full_hash_known:
                try:
                    c_full_hash = get_hash(c, first_chunk_only=False)
                    self.file_for_full_hash[c_full_hash] = c
                    self.full_hash_known.add(c)
                except OSError:
                    pass

        full_hash = get_hash(path, first_chunk_only=False)
        duplicate = self.file_for_full_hash.get(full_hash)
        if duplicate:
            return {"duplicate": duplicate}
        self.file_for_full_hash[full_hash] = path
        return False

    def pipeline(self, args):
        return self.matches(str(fullpath(args["path"])))

    def __str__(self) -> str:
        return "Duplicate()"
