import logging
import os
from datetime import datetime
from typing import Iterable, NamedTuple

import fs
from fs.base import FS
from fs.walk import Walker
from schema import SchemaError

from .actions import ALL as ACTIONS
from .actions.action import Action
from .filters import ALL as FILTERS
from .filters.filter import Filter
from .output import RichOutput, console
from .utils import deep_merge_inplace

logger = logging.getLogger(__name__)


class Location(NamedTuple):
    walker: Walker
    base_fs: FS
    path: str


output_helper = RichOutput()

DEFAULT_SYSTEM_EXCLUDE_FILES = [
    "thumbs.db",
    "desktop.ini",
    "~$*",
    ".DS_Store",
    ".localized",
]

DEFAULT_SYSTEM_EXCLUDE_DIRS = [
    ".git",
    ".svn",
]


def walker_args_from_location_options(options):
    # combine system_exclude and exclude into a single list
    excludes = options.get("system_exlude_files", DEFAULT_SYSTEM_EXCLUDE_FILES)
    excludes.extend(options.get("exclude_files", []))
    exclude_dirs = options.get("system_exclude_dirs", DEFAULT_SYSTEM_EXCLUDE_DIRS)
    exclude_dirs.extend(options.get("exclude_dirs", []))
    # return all the default options
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


def instantiate_location(loc):
    if isinstance(loc, str):
        loc = {"path": loc}

    if "walker" not in loc:
        args = walker_args_from_location_options(loc)
        walker = Walker(**args)
    else:
        walker = loc["walker"]

    if "fs" in loc:
        base_fs = fs.open_fs(loc["fs"])
        path = loc.get("path", "/")
    else:
        base_fs = fs.open_fs(loc["path"])
        path = "/"

    return Location(
        walker=walker,
        base_fs=base_fs,
        path=path,
    )


def instantiate_by_name(d, classes):
    if isinstance(d, str):
        return classes[d]()
    key, value = list(d.items())[0]
    if isinstance(key, str):
        Class = classes[key]
        if isinstance(value, dict):
            return Class(**value)
        return Class(value)
    return d


def replace_with_instances(config):
    for rule in config["rules"]:
        rule["locations"] = [instantiate_location(loc) for loc in rule["locations"]]
        # filters are optional
        rule["filters"] = [
            instantiate_by_name(x, FILTERS) for x in rule.get("filters", [])
        ]
        rule["actions"] = [instantiate_by_name(x, ACTIONS) for x in rule["actions"]]


def filter_pipeline(filters: Iterable[Filter], args: dict) -> bool:
    """
    run the filter pipeline.
    Returns True on a match, False otherwise and updates `args` in the process.
    """
    for filter_ in filters:
        try:
            result = filter_.pipeline(args)
            if isinstance(result, dict):
                deep_merge_inplace(args, result)
            elif not result:
                # filters might return a simple True / False.
                # Exit early if a filter does not match.
                return False
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(e)
            # console.print_exception()
            filter_.print_error(e)
            return False
    return True


def action_pipeline(actions: Iterable[Action], args: dict, simulate: bool) -> bool:
    for action in actions:
        try:
            updates = action.pipeline(args, simulate=simulate)
            # jobs may return a dict with updates that should be merged into args
            if updates is not None:
                deep_merge_inplace(args, updates)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(e)
            action.print_error(e)
            return False
    return True


def run(config, simulate: bool = True):
    count = [0, 0]
    Action.print_hook = output_helper.pipeline_message
    Action.print_error_hook = output_helper.pipeline_error
    Filter.print_hook = output_helper.pipeline_message
    Filter.print_error_hook = output_helper.pipeline_error

    if simulate:
        output_helper.print_simulation_banner()

    for rule in config["rules"]:
        target = rule.get("targets", "files")
        output_helper.print_rule(rule["name"])

        # status_verb = "simulating" if simulate else "organizing"
        # with console.status("[bold green]%s..." % status_verb) as status:
        for walker, base_fs, base_path in rule["locations"]:
            walk = walker.files if target == "files" else walker.dirs
            for path in walk(fs=base_fs, path=base_path):
                args = {
                    "fs": base_fs,
                    "fs_path": path,
                    "path": "NOT IMPLEMENTED",  # str(base_fs.getsyspath(path)),
                    "relative_path": fs.path.relativefrom(base_path, path),
                    "env": os.environ,
                    "now": datetime.now(),
                    "utcnow": datetime.utcnow(),
                }
                output_helper.set_location(base_fs, path)
                match = filter_pipeline(
                    filters=rule["filters"],
                    args=args,
                )
                if match:
                    success = action_pipeline(
                        actions=rule["actions"],
                        args=args,
                        simulate=simulate,
                    )
                    count[success] += 1

    if simulate:
        output_helper.print_simulation_banner()


if __name__ == "__main__":
    from .config import CONFIG_SCHEMA, load_from_file

    conf = load_from_file("testconf.yaml")
    try:
        console.print(CONFIG_SCHEMA.json_schema("asd"))
        CONFIG_SCHEMA.validate(conf)
        replace_with_instances(conf)
        run(conf, simulate=True)
    except SchemaError as e:
        console.print(e.autos[-1])
        console.print(e.code)
    except Exception as e:
        console.print_exception()
