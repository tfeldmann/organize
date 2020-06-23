import re
from typing import Any, Iterable, Iterator, Mapping, Text, Tuple, Union

import fs
from fs.walk import Walker

WILDCARD_REGEX = re.compile(r"(?<!\\)[\*\?\[]+")


def split_glob(pattern):
    base = []
    glob_patterns = []
    force_glob = False
    recursive = False
    for component in fs.path.iteratepath(pattern):
        if force_glob or WILDCARD_REGEX.search(component):
            if component == "**":
                recursive = True
            else:
                glob_patterns.append(component)
            force_glob = True
        else:
            base.append(component)
    return (fs.path.join(*base), fs.path.join(*glob_patterns), recursive)


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
            # TODO: "group_by_folder": False,
            # TODO: "normalize_unicode": False,
            # TODO: "case_sensitive": True,
        }
        if config:
            self.config.update(config)

    def walkers(self) -> Iterable[Tuple[Text, Walker]]:
        for entry in self.folders:
            # if only a string is given we pack it into a tuple with empty settings
            if isinstance(entry, str):
                entry = (entry, {})

            # split path into base path and glob pattern
            pattern, args = entry
            folder, glob, recursive = split_glob(pattern)

            # if a recursive glob pattern and not settings are given, adjust max_depth
            if "max_depth" not in args and recursive:
                args["max_depth"] = None

            # combine defaults and folder config
            config = self.config.copy()
            config.update(args)

            walker = Walker(
                filter=[glob] if glob else None,
                filter_dirs=None,
                exclude=list(
                    set(config["system_exclude_files"]) | set(config["exclude_files"])
                ),
                exclude_dirs=list(
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

    def run_for_file(self, path, simulate=True):
        print(path)
        for filter_ in self.filters:
            pass

    def run(self, *args, **kwargs):
        for path in self.files():
            self.run_for_file(path=path, *args, **kwargs)


def test():
    organizer = Organizer(
        folders=[
            "~/Documents/",
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
