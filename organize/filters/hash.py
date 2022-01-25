import logging

from fs.base import FS

from organize.utils import JinjaEnv

from . import Filter

logger = logging.getLogger(__name__)


class Hash(Filter):

    """
    Calculates the hash of a file.

    Args:
        algorithm (str)
        Any hashing algorithm available to python's `hashlib`.

        List the available algorithms on your installation:

        >>> import hashlib
        >>> hashlib.algorithms_guaranteed
        {'shake_256', 'sha3_256', 'sha1', 'sha3_224', 'sha384', 'sha512', 'blake2b', 'blake2s', 'sha256', 'sha224', 'shake_128', 'sha3_512', 'sha3_384', 'md5'}
        >>> hashlib.algorithms_available
        {'shake_256', 'whirlpool', 'mdc2', 'blake2s', 'sha224', 'shake_128', 'sha3_512', 'sha3_224', 'sha384', 'md5', 'sha1', 'sha512_256', 'blake2b', 'sha256', 'sha512_224', 'ripemd160', 'sha3_384', 'md4', 'sm3', 'sha3_256', 'md5-sha1', 'sha512'}

    Returns:
        {"hash": str} where str is the hash of the file.
    """

    name = "hash"

    def __init__(self, algorithm="md5"):
        self.algorithm = JinjaEnv.from_string(algorithm)

    def pipeline(self, args: dict):
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]  # type: str
        algo = self.algorithm.render(**args)
        hash_ = fs.hash(fs_path, name=algo)
        return {"hash": hash_}

    def __str__(self) -> str:
        return "Hash(algorithm={})".format(self.algorithm)
