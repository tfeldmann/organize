from pydantic import Field
import logging

from fs.base import FS
from typing_extensions import Literal

from organize.utils import Template

from .filter import Filter, FilterResult

logger = logging.getLogger(__name__)


class Hash(Filter):

    """Calculates the hash of a file.

    Args:
        algorithm (str): Any hashing algorithm available to python's `hashlib`.
            `md5` by default.

    Algorithms guaranteed to be available are
    `shake_256`, `sha3_256`, `sha1`, `sha3_224`, `sha384`, `sha512`, `blake2b`,
    `blake2s`, `sha256`, `sha224`, `shake_128`, `sha3_512`, `sha3_384` and `md5`.

    Depending on your python installation and installed libs there may be additional
    hash algorithms to chose from.

    To list the available algorithms on your installation run this in a python
    interpreter:

    ```py
    >>> import hashlib
    >>> hashlib.algorithms_available
    {'shake_256', 'whirlpool', 'mdc2', 'blake2s', 'sha224', 'shake_128', 'sha3_512', 'sha3_224', 'sha384', 'md5', 'sha1', 'sha512_256', 'blake2b', 'sha256', 'sha512_224', 'ripemd160', 'sha3_384', 'md4', 'sm3', 'sha3_256', 'md5-sha1', 'sha512'}
    ```

    **Returns:**

    - `{hash}`:  The hash of the file.
    """

    name: Literal["hash"] = Field("hash", repr=False)
    algorithm: str = "md5"

    _algorithm: Template

    class ParseConfig:
        accepts_positional_arg = "algorithm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._algorithm = Template.from_string(self.algorithm)

    def pipeline(self, args: dict):
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]  # type: str
        algo = self._algorithm.render(**args)
        hash_ = fs.hash(fs_path, name=algo)
        return FilterResult(
            matches=True,
            updates={self.name: hash_},
        )
