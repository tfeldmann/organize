from typing import Any, Iterable, Iterator, Mapping, Text, Union, Tuple

import fs  # type: ignore
from fs.walk import Walker


class Organizer:
    def __init__(self, folders, filters=None, actions=None, config=None):
        self.folders = folders
        self.filters = filters or []
        self.actions = actions or []

        self.config = {
            "exclude_dirs": (),
            "exclude_files": (),
            "system_exclude_dirs": (".git", ".svn", ".venv", ".pio"),
            "system_exclude_files": (
                "thumbs.db",
                "desktop.ini",
                "~$*",
                ".DS_Store",
                ".localized",
            ),
            "max_depth": 0,
            "search": "breadth",
            "ignore_errors": False,
            # TODO: "normalize_unicode": False,
            # TODO: "case_sensitive": True,
        }
        if config:
            self.config.update(config)

    def walkers(self) -> Iterable[Tuple[Text, Walker]]:
        for entry in self.folders:
            if isinstance(entry, str):
                entry = (entry, {})

            folder, args = entry
            config = self.config.copy()
            config.update(args)

            walker = Walker(
                filter=None,
                filter_dirs=None,
                exclude=(
                    set(config["system_exclude_files"]) | set(config["exclude_files"])
                ),
                exclude_dirs=(
                    set(config["system_exclude_dirs"]) | set(config["exclude_dirs"])
                ),
                ignore_errors=config["ignore_errors"],
                max_depth=config["max_depth"],
                search=config["search"],
            )
            yield (folder, walker)

    def files(self) -> Iterator[Text]:
        for path, walker in self.walkers():
            folder_fs = fs.open_fs(path)
            yield from walker.files(folder_fs)

    def run(self, simulate=True):
        for f in self.files():
            print(f)


def test():
    organizer = Organizer(
        folders=[
            "~/Documents",
            ("~/Downloads/", {"max_depth": None}),
            ("~/Documents", {}),
        ],
        filters=[],
        actions=[],
    )
    for path, walker in organizer.walkers():
        print(path, walker)
    if input("run? [Y/n]").lower() != "n":
        organizer.run(simulate=True)


if __name__ == "__main__":
    test()
