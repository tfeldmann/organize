import hashlib
from pathlib import Path
from typing import ClassVar

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.template import Template, render


def hash(path: Path, algo: str, *, _bufsize=2**18) -> str:
    # Future: for python >= 3.11 we can use hashlib.file_digest
    h = hashlib.new(algo)
    buf = bytearray(_bufsize)
    view = memoryview(buf)
    with open(path, "rb", buffering=0) as f:
        while size := f.readinto(view):
            h.update(view[:size])
    return h.hexdigest()


def hash_first_chunk(path: Path, algo: str, *, chunksize=1024) -> str:
    h = hashlib.new(algo)
    with path.open("rb") as f:
        chunk = f.read(chunksize)
        h.update(chunk)
    return h.hexdigest()


@dataclass(config=ConfigDict(extra="forbid"))
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

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="hash",
        files=True,
        dirs=False,
    )

    def __post_init__(self):
        self._algorithm = Template.from_string(self.algorithm)

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None
        algo = render(self._algorithm, res.dict()).lower()
        result = hash(path=res.path, algo=algo)
        res.vars[self.filter_config.name] = result
        return True
