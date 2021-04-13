import mimetypes

from organize.compat import Path
from organize.utils import DotDict, flatten

from .filter import Filter


class MimeType(Filter):

    """
    Filter by MIME type associated with the file extension
    """

    def __init__(self, *mimetypes):
        self.mimetypes = list(map(str.lower, flatten(list(mimetypes))))

    @staticmethod
    def mimetype(path):
        type_, _ = mimetypes.guess_type(path, strict=False)
        return type_

    def matches(self, path: Path):
        mimetype = self.mimetype(path)
        if mimetype is None:
            return False
        if not self.mimetypes:
            return True
        return any(mimetype.startswith(x) for x in self.mimetypes)

    def pipeline(self, args: DotDict):
        if self.matches(args.path):
            result = self.mimetype(args.path)
            return {"mimetype": result}
        return None

    def __str__(self):
        return "MimeType(%s)" % ", ".join(self.mimetypes)
