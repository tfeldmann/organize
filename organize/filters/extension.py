from organize.utils import flatten
from .filter import Filter


class ExtensionResult:

    def __init__(self, ext):
        self.ext = ext if ext.startswith('.') else '.%s' % ext

    @property
    def lower(self):
        return self.ext.lower()

    @property
    def upper(self):
        return self.ext.upper()

    def __str__(self):
        return self.ext


class Extension(Filter):

    """
    Filter by file extension

    :param extensions:
        The file extensions to match (does not need to start with a colon).

    :returns:
        - `{extension}`: the original file extension including colon.
        - `{extension.lower}`: the file extension in lowercase including colon.
        - `{extension.upper}`: the file extension in UPPERCASE including colon.

    Examples:

        - Match a single file extension:

          .. code-block:: yaml

            # config.yaml
            rules:
              - folders: '~/Desktop'
                filters:
                  - Extension: png
                actions:
                  - Echo: 'Found PNG file: {path}'

        - Match multiple file extensions:

          .. code-block:: yaml

            # config.yaml
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

            # config.yaml
            rules:
              - folder: '~/Desktop'
                filters:
                  - Extension
                actions:
                  - Rename: '{path.stem}{extension.lower}'

        - Using extension lists:

          .. code-block:: yaml

            # config.yaml
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
            map(self.normalize_extension, flatten(list(extensions))))

    @staticmethod
    def normalize_extension(ext):
        return ext.lower() if ext.startswith('.') else '.%s' % ext.lower()

    def matches(self, path):
        return not self.extensions or path.suffix.lower() in self.extensions

    def parse(self, path):
        result = ExtensionResult(path.suffix)
        return {'extension': result}

    def __str__(self):
        return 'Extension(%s)' % ', '.join(self.extensions)
