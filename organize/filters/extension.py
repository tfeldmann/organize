from collections import namedtuple
from organize.helpers import flatten
from .filter import Filter

ExtensionResult = namedtuple('ExtensionResult', 'lower upper')


class Extension(Filter):

    """
    Filter by file extension

    :param extensions:
        The file extensions to match (do not need to start with a colon).

    :returns:
        - `extension.lower` - the file extension including colon in lowercase
        - `extension.upper` - the file extension including colon in UPPERCASE

    Examples:
        - Match a single file extension:

          .. code-block:: yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - Extension: png
                actions:
                  - Echo: 'Found PNG file: {path}'

        - Match multiple file extensions:

          .. code-block:: yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - Extension:
                    - jpg
                    - jpeg
                actions:
                  - Echo: 'Found JPG file: {path}'

        - Make all file extensions lowercase:

          .. code-block:: yaml

            rules:
              - folder: '~/Desktop'
                filters:
                  - Extension
                actions:
                  - Rename: '{path.stem}{extension.lower}'

        - Using extension lists:

          .. code-block:: yaml

            img_ext: &img
              - png
              - jpg
              - tiff

            audio_ext: &audio
              - mp3
              - wav
              - ogg

            rules:
              - folders: '~/Desktop'
                filters:
                  - Extension:
                    - *img
                    - *audio
                actions:
                  - Echo: 'Found media file: {path}'
    """

    def __init__(self, *extensions):
        self.extensions = list(
            map(self.normalize_extension, flatten(extensions)))

    @staticmethod
    def normalize_extension(ext):
        if ext.startswith('.'):
            return ext.lower()
        else:
            return '.%s' % ext.lower()

    def matches(self, path):
        return not self.extensions or path.suffix.lower() in self.extensions

    def parse(self, path):
        ext = self.normalize_extension(path.suffix)
        return {
            'extension': ExtensionResult(lower=ext, upper=ext.upper())
        }

    def __str__(self):
        return 'Extension(%s)' % ', '.join(self.extensions)
