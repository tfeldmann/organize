from fs.base import FS

from .filter import Filter


class Empty(Filter):

    """Finds empty dirs and files"""

    name = "empty"

    @classmethod
    def get_schema(cls):
        return cls.name

    def pipeline(self, args: dict):
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]  # type: str

        if fs.isdir(fs_path):
            return fs.isempty(fs_path)
        return fs.getsize(fs_path) == 0

    def __str__(self) -> str:
        return "Empty()"
