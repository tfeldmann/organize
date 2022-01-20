import fs
from rich.console import Console

console = Console()


def walker_args_from_options(options):
    excludes = options.get(
        "system_exlude_files",
        [
            "thumbs.db",
            "desktop.ini",
            "~$*",
            ".DS_Store",
            ".localized",
        ],
    )
    excludes.extend(options.get("exclude_files", []))
    exclude_dirs = options.get(
        "system_exclude_dirs",
        [
            "*.git",
            "*.svn",
            ".venv",
            ".pio",
        ],
    )
    exclude_dirs.extend(options.get("exclude_dirs", []))

    return {
        "ignore_errors": options.get("ignore_errors", False),
        "on_error": options.get("on_error", None),
        "search": options.get("search", "depth"),
        "exclude": excludes,
        "exclude_dirs": exclude_dirs,
        "max_depth": options.get("max_depth", None),
        "filter": None,
        "filter_dirs": None,
    }


config = {
    "version": 1,
    "rules": [
        {
            "name": "Fixup old pdfs",
            "targets": "files",
            "locations": [
                {
                    "path": "~/Desktop",
                    "max_depth": 3,
                },
            ],
            "filters": [
                {
                    "extension": "pdf",
                },
            ],
            "actions": [
                {
                    "copy": "~/Dir",
                },
            ],
        },
        {
            "name": "Find some folders",
            "targets": "dirs",
            "locations": [
                {
                    "path": "~/Desktop",
                    "max_depth": 10,
                },
                {
                    "path": "~/Desktop/Inbox",
                    "max_depth": None,
                },
            ],
            "filters": [
                {
                    "extension": "pdf",
                },
            ],
            "actions": [
                {
                    "copy": "~/Dir",
                },
            ],
        },
    ],
}


def instantiate_entry(d, classes):
    key, value = list(d.items())[0]
    if isinstance(key, str):
        Class = classes[key.lower()]
        if isinstance(value, dict):
            return Class(**value)
        return Class(value)
    return {key: value}


def instantiate_in_place(config):
    for rule in config["rules"]:
        rule["filters"] = [instantiate_entry(x, FILTERS) for x in rule["filters"]]
        rule["actions"] = [instantiate_entry(x, ACTIONS) for x in rule["actions"]]


def run(config):
    for rule in config["rules"]:
        target = rule.get("targets", "files")
        console.print(rule["name"], style="bold")
        with console.status("[bold green]organizing...") as status:
            for location in rule["locations"]:
                path = location["path"]
                folder_fs = fs.open_fs(path)
                walker_args = walker_args_from_options(location)
                if target == "files":
                    for path in folder_fs.walk.files(**walker_args):
                        if ".html" in path:
                            console.print(folder_fs, path)
                elif target == "dirs":
                    for path in folder_fs.walk.dirs(**walker_args):
                        if "PrintQueue" in path:
                            console.print(folder_fs, path)


if __name__ == "__main__":
    instantiate_in_place(config)
    print(config)
    run(config)
