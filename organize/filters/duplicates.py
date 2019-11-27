# https://stackoverflow.com/a/36113168/300783
import hashlib
import os
import sys
from collections import defaultdict

from organize.compat import Path
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


class Duplicates(Filter):
    def __init__(self) -> None:
        self.files_by_size = defaultdict(list)
        self.files_by_small_hash = defaultdict(list)
        self.files_by_full_hash = dict()

        # we keep track of which files we already computed the hashes for so we only do
        # that once.
        self.small_hash_known = set()

    def register_small_hash(self, path):
        if path not in self.small_hash_known:
            small_hash = get_hash(path, first_chunk_only=True)
            self.files_by_small_hash[small_hash].append(path)
            self.small_hash_known.add(path)
            return small_hash
        return None  # already registered

    def register_full_hash(self, path):
        full_hash = get_hash(path, first_chunk_only=False)
        duplicate = self.files_by_full_hash.get(full_hash)
        if duplicate:
            return duplicate
        self.files_by_full_hash[full_hash] = path
        return None

    def matches(self, path: str):
        filepath = fullpath(path)
        file_size = filepath.stat().st_size

        # Check for files with similar size
        same_size = self.files_by_size[file_size]
        candidates_fsize = same_size[:]
        same_size.append(filepath)
        if not candidates_fsize:
            # the file is unique in size and cannot be a duplicate
            return False

        # For all other files with the same file size, get their hash of the first 1024
        # bytes
        for candidate in candidates_fsize:
            self.register_small_hash(candidate)
        small_hash = self.register_small_hash(filepath)
        if not small_hash:
            # the file has already been handled.
            return False

        candidates_small = self.files_by_small_hash[small_hash][:-1]
        for candidate in candidates_small:
            self.register_full_hash(candidate)
        duplicate = self.register_full_hash(filepath)
        if duplicate:
            return {"duplicates": {"file1": filepath, "file2": duplicate}}

    def pipeline(self, args):
        return self.matches(str(fullpath(args["path"])))

    def __str__(self) -> str:
        return "Duplicates()"
