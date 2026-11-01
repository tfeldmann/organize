import plistlib
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, ClassVar, Dict, Optional

from pydantic.config import ConfigDict
from pydantic.dataclasses import dataclass

from organize.filter import FilterConfig
from organize.logger import logger
from organize.output import Output
from organize.resource import Resource
from organize.utils import safe_path_part

FIELDS = ("title", "artist", "album", "genre", "year", "track", "duration")

# Tag names used by the different formats, in order of preference.
TAG_NAMES = {
    "title": ("title", "TIT2", "\xa9nam"),
    "artist": ("artist", "albumartist", "TPE1", "TPE2", "\xa9ART", "aART"),
    "album": ("album", "TALB", "\xa9alb"),
    "genre": ("genre", "TCON", "\xa9gen"),
    "year": ("date", "year", "TDRC", "TYER", "\xa9day"),
    "track": ("tracknumber", "TRCK", "trkn"),
}

SPOTLIGHT_ATTRS = {
    "title": "kMDItemTitle",
    "artist": "kMDItemAuthors",
    "album": "kMDItemAlbum",
    "genre": "kMDItemMusicalGenre",
    "year": "kMDItemRecordingYear",
    "duration": "kMDItemDurationSeconds",
}


def _first(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        value = value[0] if value else ""
    if isinstance(value, tuple):  # mp4 track numbers are (nr, total)
        value = value[0]
    return str(value).strip()


def _from_mutagen(path: Path) -> Dict[str, str]:
    import mutagen

    try:
        media = mutagen.File(path)
    except Exception as e:
        logger.debug("mutagen could not read %s: %s", path, e)
        return {}
    if media is None:
        return {}

    result: Dict[str, str] = {}
    tags = media.tags or {}
    for field, names in TAG_NAMES.items():
        for name in names:
            try:
                value = tags.get(name)
            except (ValueError, KeyError):
                value = None
            if value:
                text = _first(getattr(value, "text", value))
                if text:
                    result[field] = text
                    break
    length = getattr(media.info, "length", None)
    if length:
        result["duration"] = str(round(length))
    return result


def _from_spotlight(path: Path) -> Dict[str, str]:
    # macOS indexes metadata of most media formats, including those mutagen can't read
    if sys.platform != "darwin":
        return {}
    args = ["mdls", "-plist", "-"]
    for attr in SPOTLIGHT_ATTRS.values():
        args += ["-name", attr]
    try:
        out = subprocess.run(
            [*args, str(path)], capture_output=True, timeout=10, check=True
        ).stdout
        values = plistlib.loads(out)
    except (OSError, subprocess.SubprocessError, plistlib.InvalidFileException):
        return {}
    result: Dict[str, str] = {}
    for field, attr in SPOTLIGHT_ATTRS.items():
        value = values.get(attr)
        if value in (None, "", []):
            continue
        if field == "duration":
            result[field] = str(round(float(value)))
        else:
            result[field] = _first(value)
    return result


def media_metadata(path: Path) -> Dict[str, str]:
    """Returns the available metadata of an audio or video file."""
    result = _from_mutagen(path)
    if len(result) < len(FIELDS):
        for key, value in _from_spotlight(path).items():
            result.setdefault(key, value)
    if "year" in result:
        m = re.search(r"\d{4}", result["year"])
        if m:
            result["year"] = m.group(0)
        else:
            del result["year"]
    if "track" in result:
        result["track"] = result["track"].split("/")[0]
    return result


def describe(meta: Dict[str, str]) -> Optional[str]:
    """A human readable summary used in AI prompts."""
    if not meta:
        return None
    unit = {"duration": " seconds"}
    lines = [
        f"{key.capitalize()}: {meta[key]}{unit.get(key, '')}"
        for key in FIELDS
        if key in meta
    ]
    return "\n".join(lines)


@dataclass(config=ConfigDict(extra="forbid"))
class Media:
    """Reads metadata of audio and video files (like ID3 or MP4 tags).

    On macOS, metadata of formats without readable tags is taken from Spotlight.
    Files without any metadata do not match.

    **Returns:**

    - `{media.title}`, `{media.artist}`, `{media.album}`, `{media.genre}`:
      The tag values, made safe to use in paths (`Unknown` if missing)
    - `{media.year}`: The recording year (`Unknown` if missing)
    - `{media.track}`: The track number (`Unknown` if missing)
    - `{media.duration}`: The length in seconds (`0` if unknown)

    You can show the metadata of a file by running:

    ```sh
    python -m organize.filters.media "/path/to/file.mp3"
    ```
    """

    filter_config: ClassVar[FilterConfig] = FilterConfig(
        name="media",
        files=True,
        dirs=False,
    )

    def pipeline(self, res: Resource, output: Output) -> bool:
        assert res.path is not None, "Does not support standalone mode"
        meta = media_metadata(res.path)
        values = {key: safe_path_part(meta.get(key, "")) for key in FIELDS}
        values["duration"] = meta.get("duration", "0")
        res.vars[self.filter_config.name] = values
        return bool(meta)


if __name__ == "__main__":
    import json

    print(json.dumps(media_metadata(Path(sys.argv[1])), indent=2))
