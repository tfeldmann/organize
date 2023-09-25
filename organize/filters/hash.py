from typing import ClassVar

from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.utils import Template


@dataclass
class Hash:

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
    {'shake_256', 'whirlpool', 'mdc2', 'blake2s', 'sha224', 'shake_128', 'sha3_512',
    'sha3_224', 'sha384', 'md5', 'sha1', 'sha512_256', 'blake2b', 'sha256',
    'sha512_224', 'ripemd160', 'sha3_384', 'md4', 'sm3', 'sha3_256', 'md5-sha1',
    'sha512'}
    ```

    **Returns:**

    - `{hash}`:  The hash of the file.
    """

    algorithm: str = "md5"

    filter_config: ClassVar = FilterConfig(name="hash", files=True, dirs=False)

    def __post_init__(self):
        self._algorithm = Template.from_string(self.algorithm)

    def pipeline(self, res: Resource, output: Output) -> bool:
        algo = self._algorithm.render(**res.dict()).lower()
        hash = res.hash(algo=algo)
        res.vars[self.filter_config.name] = hash
        return True
