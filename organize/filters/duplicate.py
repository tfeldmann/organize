"""
Duplicate detection filter.

Based on this stackoverflow answer:
    https://stackoverflow.com/a/36113168/300783

Which was updated for python3 in:
    https://gist.github.com/tfeldmann/fc875e6630d11f2256e746f67a09c1ae

The script on stackoverflow has a bug which could lead to false positives. This is fixed
here by using a tuple (file_size, hash) as key in the comparison dictionaries.
"""
import hashlib
import os
from collections import defaultdict
from typing import DefaultDict as DDict
from typing import Dict, List, Set, Tuple, Union

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
    Finds duplicate files.

    This filter compares files byte by byte and finds identical files with potentially
    different filenames.

    :returns:
        - ``{duplicate}`` -- path to the duplicate source

    Examples:
        - Show all duplicate files in your desktop and download folder (and their
          subfolders).

          .. code-block:: yaml
            :caption: config.yaml

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

        # to prevent false positives the keys must be tuples of (file_size, hash).
        self.files_for_small_hash = defaultdict(
            list
        )  # type: DDict[Tuple[int, bytes], List[str]]
        self.file_for_full_hash = dict()  # type: Dict[Tuple[int, bytes], str]

        # we keep track of which files we already computed the hashes for so we only do
        # that once.
        self.small_hash_known = set()  # type: Set[str]
        self.full_hash_known = set()  # type: Set[str]

    def matches(self, path: str) -> Union[bool, Dict[str, str]]:
        # the exact same path has already been handled. This might happen if path is a
        # symlink which resolves to file that is already known. We skip these.
        if path in self.small_hash_known:
            return False

        # check for files with equal size
        file_size = os.path.getsize(path)  # type: int
        same_size = self.files_for_size[file_size]
        candidates_fsize = same_size[:]
        same_size.append(path)
        if not candidates_fsize:
            # the file is unique in size and cannot be a duplicate
            return False

        # for all other files with the same file size, get their hash of the first 1024
        # bytes
        for c in candidates_fsize:
            if c not in self.small_hash_known:
                try:
                    c_small_hash = get_hash(c, first_chunk_only=True)
                    self.files_for_small_hash[(file_size, c_small_hash)].append(c)
                    self.small_hash_known.add(c)
                except OSError:
                    pass

        # check small hash collisions with the current file
        small_hash = get_hash(path, first_chunk_only=True)
        same_small_hash = self.files_for_small_hash[(file_size, small_hash)]
        candidates_shash = same_small_hash[:]
        same_small_hash.append(path)
        self.small_hash_known.add(path)
        if not candidates_shash:
            # the file has a unique small hash and cannot be a duplicate
            return False

        # For all other files with the same file size and small hash get the full hash
        for c in candidates_shash:
            if c not in self.full_hash_known:
                try:
                    c_full_hash = get_hash(c, first_chunk_only=False)
                    self.file_for_full_hash[(file_size, c_full_hash)] = c
                    self.full_hash_known.add(c)
                except OSError:
                    pass

        # check full hash collisions with the current file
        full_hash = get_hash(path, first_chunk_only=False)
        duplicate = self.file_for_full_hash.get((file_size, full_hash))
        if duplicate:
            return {"duplicate": duplicate}
        self.file_for_full_hash[(file_size, full_hash)] = path
        return False

    def pipeline(self, args):
        return self.matches(str(fullpath(args["path"])))

    def __str__(self) -> str:
        return "Duplicate()"
