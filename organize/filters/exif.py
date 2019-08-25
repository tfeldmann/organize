import collections

import exifread

from .filter import Filter


class Exif(Filter):

    """
    Filter by EXIF data
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def convert_tags(self, tags):
        result = collections.defaultdict(dict)
        for key, value in tags.items():
            if " " in key:
                category, field = key.split(" ", maxsplit=1)
                result[category][field] = value.printable
            else:
                result[key] = value.printable
        return result

    def matches(self, path):
        with path.open("rb") as f:
            exiftags = exifread.process_file(f, details=False)
            if not exiftags:
                return False

            tags = {k.lower(): v for k, v in exiftags.items()}
            if tags:
                for key, _ in self.kwargs.items():
                    if key.lower() not in tags:
                        return False
                return self.convert_tags(tags)

    def pipeline(self, args):
        tags = self.matches(args.path)
        if tags:
            return {"exif": tags}

    def __str__(self):
        return "EXIF(%s)" % ", ".join(self.kwargs.items())
