import collections

import exifread

from .filter import Filter


class Exif(Filter):

    """
    Filter by EXIF data
    """

    def __init__(self, *args, **kwargs):
        self.args = args  # expected exif keys
        self.kwargs = kwargs  # exif keys with expected values

    def category_dict(self, tags):
        result = collections.defaultdict(dict)
        for key, value in tags.items():
            if " " in key:
                category, field = key.split(" ", maxsplit=1)
                result[category][field] = value
            else:
                result[key] = value
        return result

    def matches(self, path):
        with path.open("rb") as f:
            exiftags = exifread.process_file(f, details=False)
        if not exiftags:
            return False

        tags = {k.lower(): v.printable for k, v in exiftags.items()}

        # no match if expected tag is not found
        normkey = lambda k: k.replace(".", " ").lower()
        for key in self.args:
            if normkey(key) not in tags:
                return False
        # no match if tag has not expected value
        for key, value in self.kwargs.items():
            key = normkey(key)
            if not (key in tags and tags[key].lower() == value.lower()):
                return False
        return self.category_dict(tags)

    def pipeline(self, args):
        tags = self.matches(args.path)
        if tags:
            return {"exif": tags}

    def __str__(self):
        return "EXIF(%s)" % ", ".join(self.kwargs.items())
