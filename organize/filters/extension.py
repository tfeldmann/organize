from typing import Dict, Optional, Union

from pathlib import Path
from organize.utils import DotDict, flatten

from .filter import Filter


class ExtensionResult:
    def __init__(self, ext):
        self.ext = ext[1:] if ext.startswith(".") else ext

    @property
    def lower(self):
        return self.ext.lower()

    @property
    def upper(self):
        return self.ext.upper()

    def __str__(self):
        return self.ext


class Extension(Filter):
    name = "extension"

    """
    Filter by file extension

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

    def pipeline(self, args: dict):
        fs = args["fs"]
        fs_path = args["fs_path"]
        suffix = fs.getinfo(fs_path).suffix
        if self.matches(suffix):
            result = ExtensionResult(suffix)
            return {"extension": result}
        return None

    def __str__(self):
        return "Extension(%s)" % ", ".join(self.extensions)
