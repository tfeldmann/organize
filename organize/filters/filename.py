from .filter import Filter


class Filename(Filter):

    def __init__(self, startswith='', contains='', endswith='',
                 case_sensitive=True):
        self.startswith = startswith
        self.contains = contains
        self.endswith = endswith
        self.case_sensitive = case_sensitive

        if not self.case_sensitive:
            self.startswith = self.startswith.lower()
            self.contains = self.contains.lower()
            self.endswith = self.endswith.lower()

    def matches(self, path):
        filename = self._filename(path)
        return (
            filename.startswith(self.startswith) and
            filename.endswith(self.endswith) and
            self.contains in filename)

    def _filename(self, path):
        if not self.case_sensitive:
            return path.stem.lower()
        else:
            return path.stem
