from typing import Union

from fs.base import FS

from organize.utils import flatten

from .filter import Filter, FilterResult


class Extension(Filter):
    """Filter by file extension

    Args:
        *extensions (list(str) or str):
            The file extensions to match (does not need to start with a colon).

    **Returns:**

    - `{extension}`: the original file extension (without colon)
    """

    name = "extension"
    schema_support_instance_without_args = True

    def __init__(self, *extensions) -> None:
        self.extensions = list(map(self.normalize_extension, flatten(list(extensions))))

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
            updates={self.get_name(): ext},
        )

    def __str__(self):
        return f"Extension({', '.join(self.extensions)})"
