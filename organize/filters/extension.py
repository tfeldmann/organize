from typing import List, Union

from fs.base import FS
from pydantic import Field, validator
from typing_extensions import Literal

from organize.utils import flatten

from .filter import Filter, FilterResult


def convert_to_list(cls, v):
    if not v:
        return []
    if isinstance(v, str):
        return v.split()
    return v


def ensure_list(field_name: str):
    return validator(field_name, allow_reuse=True, pre=True)(convert_to_list)


class Extension(Filter):
    """Filter by file extension

    Args:
        *extensions (list(str) or str):
            The file extensions to match (does not need to start with a colon).

    **Returns:**

    - `{extension}`: the original file extension (without colon)
    """

    name: Literal["extension"] = "extension"
    extensions: Union[List[str], str] = Field(default_factory=list)

    _validate_extensions = ensure_list("extensions")

    class ParseConfig:
        accepts_positional_arg = "extensions"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extensions = list(
            map(self.normalize_extension, flatten(list(self.extensions)))
        )

    @staticmethod
    def normalize_extension(ext: str) -> str:
        """strip colon and convert to lowercase"""
        if ext.startswith("."):
            return ext[1:].lower()
        else:
            return ext.lower()

    def matches(self, ext: str) -> Union[bool, str]:
        if not self.extensions:
            return True
        if not ext:
            return False
        return self.normalize_extension(ext) in self.extensions

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]
        if fs.isdir(fs_path):
            raise ValueError("Dirs not supported")

        # suffix is the extension with dot
        suffix = fs.getinfo(fs_path).suffix
        ext = suffix[1:]
        return FilterResult(
            matches=bool(self.matches(ext)),
            updates={self.name: ext},
        )
