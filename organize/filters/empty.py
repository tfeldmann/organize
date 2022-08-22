from fs.base import FS
from typing_extensions import Literal

from .filter import Filter, FilterResult


class Empty(Filter):

    """Finds empty dirs and files"""

    name: Literal["empty"] = "empty"

    class Config:
        accepts_positional_arg = "match"

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]  # type: str

        if fs.isdir(fs_path):
            result = fs.isempty(fs_path)
        else:
            result = fs.getsize(fs_path) == 0

        return FilterResult(matches=result, updates={})

    def __str__(self) -> str:
        return "Empty()"
