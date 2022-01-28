from typing import Union

from fs.base import FS

from organize.utils import flatten

from .filter import Filter, FilterResult


class Extension(Filter):
    """Filter by file extension

    :param extensions:
        The file extensions to match (does not need to start with a colon).

    :returns:
        - ``{extension}`` -- the original file extension (without colon)
        - ``{extension.lower}`` -- the file extension in lowercase
        - ``{extension.upper}`` -- the file extension in UPPERCASE

    Examples:
        - Match a single file extension:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - extension: png
                actions:
                  - echo: 'Found PNG file: {path}'

        - Match multiple file extensions:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - extension:
                    - .jpg
                    - jpeg
                actions:
                  - echo: 'Found JPG file: {path}'

        - Make all file extensions lowercase:

          .. code-block:: yaml
            :caption: config.yaml

            rules:
              - folders: '~/Desktop'
                filters:
                  - extension
                actions:
                  - rename: '{path.stem}.{extension.lower}'

        - Using extension lists:

          .. code-block:: yaml
            :caption: config.yaml

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
                  - extension:
                    - *img
                    - *audio
                actions:
                  - echo: 'Found media file: {path}'
    """

    name = "extension"
    schema_support_instance_without_args = True

    def __init__(self, *extensions) -> None:
        self.extensions = list(map(self.normalize_extension, flatten(list(extensions))))

    @staticmethod
    def normalize_extension(ext: str) -> str:
        """strip colon and convert to lowercase"""
        if ext.startswith("."):
            return ext[1:].lower()
        else:
            return ext.lower()

    def matches(self, suffix: str) -> Union[bool, str]:
        if not self.extensions:
            return True
        if not suffix:
            return False
        return self.normalize_extension(suffix) in self.extensions

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]
        if fs.isdir(fs_path):
            raise ValueError("Dirs not supported")

        # suffix is the extension with dot
        suffix = fs.getinfo(fs_path).suffix
        ext = suffix[1:]
        return FilterResult(
            matches=bool(self.matches(ext)),
            updates={self.get_name(): ext},
        )

    def __str__(self):
        return "Extension(%s)" % ", ".join(self.extensions)
