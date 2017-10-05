from .filter import Filter


class FileExtension(Filter):

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
