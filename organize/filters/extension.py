from .filter import Filter


class ExtensionResult:

    def __init__(self, extension):
        self.extension = extension

    def __str__(self):
        return self.extension

    @property
    def upper(self):
        return self.extension.upper()

    @property
    def lower(self):
        return self.extension.lower()


class Extension(Filter):

    """
    Filter by file extension

    :param extensions:
        The file extensions to match (do not need to start with a colon).

    :returns:
        - `extension` - the file extension including colon
        - `extension.lower` - the file extension including colon in lower case
        - `extension.upper` - the file extension including colon in upper case
    """

    def __init__(self, *extensions):
        self.extensions = list(map(self.normalize_extension, extensions))

    @staticmethod
    def normalize_extension(ext):
        if ext.startswith('.'):
            return ext.lower()
        else:
            return ''.join(['.', ext.lower()])

    def matches(self, path):
        return not self.extensions or path.suffix.lower() in self.extensions

    def parse(self, path):
        ext = self.normalize_extension(path.suffix)
        Result = ExtensionResult(ext)

        return {
            'extension': Result
        }

    def __str__(self):
        return 'FileExtension(%s)' % ', '.join(self.extensions)
