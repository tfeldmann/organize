import logging

from fs.base import FS

from organize.utils import JinjaEnv

from .filter import Filter

logger = logging.getLogger(__name__)


class Hash(Filter):

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
