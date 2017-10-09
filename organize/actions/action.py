from pathlib import Path


class Action:

    def run(self, path: Path, file_attributes: dict, simulate: bool):
        # if you change the file path, return the new path here
        raise NotImplementedError

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<%s>' % str(self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
