from typing import ClassVar, Dict, Optional

from pydantic import Field
from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.output import Output
from organize.resource import Resource
from organize.validators import FlatList

from .mimetype import guess_mimetype

GROUPS: Dict[str, str] = {}
for _group, _extensions in {
    "Documents": "pdf doc docx odt rtf txt md pages tex",
    "Spreadsheets": "xls xlsx xlsm ods csv tsv numbers",
    "Presentations": "ppt pptx odp key",
    "Ebooks": "epub mobi azw azw3",
    "Images": "jpg jpeg png gif webp heic heif tif tiff bmp svg ico psd raw cr2 nef arw dng",
    "Videos": "mp4 m4v mov avi mkv webm wmv flv mpg mpeg",
    "Audio": "mp3 m4a aac wav aiff flac ogg opus wma",
    "Archives": "zip rar 7z tar gz tgz bz2 xz",
    "Installers": "app dmg pkg mpkg exe msi deb rpm apk iso",
    "Code": "py ipynb js ts html css json xml yaml yml sh swift c cpp h java go rs rb php sql",
    "Fonts": "ttf otf woff woff2",
}.items():
    for _ext in _extensions.split():
        GROUPS[_ext] = _group

MIMETYPE_GROUPS = {
    "image": "Images",
    "video": "Videos",
    "audio": "Audio",
    "text": "Documents",
    "font": "Fonts",
}

FALLBACK_GROUP = "Other"

# used by the `ai` filter for folders that are not a bundle like `Some.app`
FOLDER_GROUP = "Folders"

ALL_GROUPS = {*GROUPS.values(), FALLBACK_GROUP, FOLDER_GROUP}


def file_group(name: str) -> str:
    _, _, ext = name.rpartition(".")
    if "." in name and ext.lower() in GROUPS:
        return GROUPS[ext.lower()]
    mimetype: Optional[str] = guess_mimetype(name)
    if mimetype:
        return MIMETYPE_GROUPS.get(mimetype.split("/")[0], FALLBACK_GROUP)
    return FALLBACK_GROUP


@dataclass(config=ConfigDict(extra="forbid"))
class FileType:
    """Groups files into broad types like Documents, Images or Archives.

    The type is determined by the file extension, falling back to the MIME type.
    Known types are Documents, Spreadsheets, Presentations, Ebooks, Images, Videos,
    Audio, Archives, Installers, Code and Fonts. Everything else is `Other`.

    Attributes:
        *types (list(str) or str): The types to filter for (case-insensitive).
            Matches all files if empty.

    **Returns:**

    - `{filetype}`: The type of the file, e.g. `Images`.
    """

    types: FlatList[str] = Field(default_factory=list)

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="filetype",
        files=True,
        dirs=False,
    )

    def matches(self, group: str) -> bool:
        if not self.types:
            return True
        return group.lower() in (x.lower() for x in self.types)

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None, "Does not support standalone mode"
        group = file_group(res.path.name)
        res.vars[self.filter_config.name] = group
        return self.matches(group)


if __name__ == "__main__":
    for ext, group in sorted(GROUPS.items(), key=lambda x: (x[1], x[0])):
        print(f"{group:15} .{ext}")
