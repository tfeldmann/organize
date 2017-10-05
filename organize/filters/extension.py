from .filter import Filter


class Extension(Filter):

    # TODO: Match a list of file extensions
    """
    Filter by file extension

    :param str ext:
        The file extension to match (does not need to start with a colon).

    :returns:
        - `extension` - the file extension including colon
        - `extension.lower` - the file extension including colon in lower case
        - `extension.upper` - the file extension including colon in upper case
    """

    def __init__(self, ext=''):
        if ext == '':
            self.ext = ''
        elif ext.startswith('.'):
            self.ext = ext.lower()
        else:
            self.ext = ''.join(['.', ext.lower()])

    def matches(self, path):
        return self.ext == '' or path.suffix.lower() == self.ext

    def parse(self, path):
        ext = path.suffix
        return {
            'extension': ext,
            'extension.lower': ext.lower(),
            'extension.upper': ext.upper(),
        }

    def __str__(self):
        return 'FileExtension("%s")' % self.ext
