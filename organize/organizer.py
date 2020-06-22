import fs


class Organizer:
    def __init__(self, folders, **kwargs):
        self._folders = folders
        self._filters = []

        self.config = {
            "exclude_dirs": [".git", ".svn", ".venv", ".pio"],
            "exclude_files": [
                "thumbs.db",
                "desktop.ini",
                ".DS_Store",
                ".localized",
                "~$*",
            ],
            "max_depth": 0,
            "search": "breadth",
        }
        self.config.update(kwargs)

    def folders(self):
        for f in self._folders:
            if isinstance(f, str):
                f = {"path": f}
            else:
                assert "path" in f, "No path specified (%s)" % f
            yield {
                "path": f["path"],
                "exclude": f.get("exclude", False),
            }

    def files(self):
        for folder in self.folders():
            folder_fs = fs.open_fs(folder["path"])
            yield from folder_fs.walk.files(
                exclude_dirs=folder.get("exclude_dirs", self.config["exclude_dirs"]),
                exclude=folder.get("exclude_files", self.config["exclude_files"]),
                max_depth=folder.get("max_depth", self.config["max_depth"]),
                search=folder.get("search", self.config["search"]),
            )

    def files_filtered(self):
        pass

    def clear_filters(self):
        self._filters = []

    def set_filters(self, filters):
        self._filters = filters

    def add_filters(self, filters):
        self._filters.extend(filters)

    def run_actions(self, actions):
        pass


def test():
    org = Organizer(
        folders=[
            {"path": "/Users/thomasfeldmann/Downloads/", "max_depth": None,},
            {"path": "~/Documents", "exclude": True},
        ],
    )

    for f in org.folders():
        print(f)

    for f in org.files():
        print(f)


if __name__ == "__main__":
    test()

# f.set_filters(
#     [filters.Extension("pdf"), filters.Filename(startswith="test"),]
# )
# f.run_actions(actions.Echo("{path}"))
