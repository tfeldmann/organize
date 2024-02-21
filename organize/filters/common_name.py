import re
from collections import Counter
from collections.abc import Iterable
from pathlib import Path
from typing import Literal


def common_names(names: Iterable[str], pattern: str, at_least: int) -> set[str]:
    ptn = re.compile(pattern)
    cnt = Counter()
    try:
        for name in names:
            if match := ptn.match(name):
                cnt[match.group(1)] += 1
    except IndexError as e:
        raise ValueError(
            f"Pattern \"{pattern}\" has no capture group (for example '(.*)\.txt')"
        ) from e
    return {key for key, val in cnt.items() if val >= at_least}


def common_path_names(
    parent: Path, targets: Literal["files", "dirs"], pattern: str, at_least: int
) -> set[str]:
    names = [
        path.name
        for path in parent.glob("*")
        if path.is_file() and targets == "files" or path.is_dir() and targets == "dirs"
    ]
    return common_names(names=names, pattern=pattern, at_least=at_least)


names = [
    "My Podcast Ep 1.mp3",
    "My Podcast Ep 2.mp3",
    "My Podcast Ep 3.mp3",
    "Your Podcast Ep 1.mp3",
    "Your Podcast Ep 2.mp3",
    "Your Podcast Ep 3.mp3",
]

print(
    common_names(
        names=names,
        pattern=r"^(.+?) Ep .+\.mp3",
        at_least=2,
    )
)
print(
    common_path_names(
        Path("~/NextCloud/Office").expanduser(),
        pattern=r"^(.)",
        targets="files",
        at_least=2,
    )
)
