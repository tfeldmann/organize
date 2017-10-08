from pathlib import Path


class Action:

    def run(self, path: Path, file_attributes: dict, simulate: bool):
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<%s>' % str(self)
