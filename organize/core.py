import logging
from collections import Counter
from pathlib import Path
from typing import Iterable, NamedTuple, Union

from fs import path as fspath
from fs.base import FS
from fs.errors import NoSysPath
from fs.walk import Walker
from rich.console import Console

from . import config, console
from .actions import ACTIONS
from .actions.action import Action
from .filters import FILTERS
from .filters.filter import Filter
from .migration import migrate_v1
from .utils import (
    basic_args,
    deep_merge_inplace,
    ensure_dict,
    ensure_list,
    fs_path_from_options,
    to_args,
)

logger = logging.getLogger(__name__)
highlighted_console = Console()


class Location(NamedTuple):
    walker: Walker
    fs: FS
    fs_path: str


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


def convert_options_to_walker_args(options: dict):
    # combine system_exclude and exclude into a single list
    excludes = options.get("system_exclude_files", DEFAULT_SYSTEM_EXCLUDE_FILES)
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


def instantiate_location(options: Union[str, dict], default_max_depth=0) -> Location:
    if isinstance(options, Location):
        return options
    if isinstance(options, str):
        options = {"path": options}

    # set default max depth from rule
    if not "max_depth" in options:
        options["max_depth"] = default_max_depth

    if "walker" not in options:
        args = convert_options_to_walker_args(options)
        walker = Walker(**args)
    else:
        walker = options["walker"]

    fs, fs_path = fs_path_from_options(
        path=options.get("path", "/"),
        filesystem=options.get("filesystem"),
    )
    return Location(walker=walker, fs=fs, fs_path=fs_path)


def instantiate_filter(filter_config):
    if isinstance(filter_config, Filter):
        return filter_config
    spec = ensure_dict(filter_config)
    name, value = next(iter(spec.items()))
    parts = name.split(maxsplit=1)
    invert = False
    if len(parts) == 2 and parts[0] == "not":
        name = parts[1]
        invert = True
    args, kwargs = to_args(value)
    instance = FILTERS[name](*args, **kwargs)
    instance.set_logic(inverted=invert)
    return instance


def instantiate_action(action_config):
    if isinstance(action_config, Action):
        return action_config
    spec = ensure_dict(action_config)
    name, value = next(iter(spec.items()))
    args, kwargs = to_args(value)
    return ACTIONS[name](*args, **kwargs)


def syspath_or_exception(fs, path):
    try:
        return Path(fs.getsyspath(path))
    except NoSysPath as e:
        return e


def replace_with_instances(config: dict):
    warnings = []

    for rule in config["rules"]:
        default_depth = None if rule.get("subfolders", False) else 0

        _locations = []
        for options in ensure_list(rule["locations"]):
            try:
                instance = instantiate_location(
                    options=options,
                    default_max_depth=default_depth,
                )
                _locations.append(instance)
            except Exception as e:
                if isinstance(options, dict) and options.get("ignore_errors", False):
                    warnings.append(str(e))
                else:
                    raise ValueError("Invalid location %s (%s)" % (options, e)) from e

        # filters are optional
        _filters = []
        for x in ensure_list(rule.get("filters", [])):
            try:
                _filters.append(instantiate_filter(x))
            except Exception as e:
                raise ValueError("Invalid filter %s (%s)" % (x, e)) from e

        # actions
        _actions = []
        for x in ensure_list(rule["actions"]):
            try:
                _actions.append(instantiate_action(x))
            except Exception as e:
                raise ValueError("Invalid action %s (%s)" % (x, e)) from e

        rule["locations"] = _locations
        rule["filters"] = _filters
        rule["actions"] = _actions

    return warnings


def filter_pipeline(filters: Iterable[Filter], args: dict, filter_mode: str) -> bool:
    """
    run the filter pipeline.
    Returns True on a match, False otherwise and updates `args` in the process.
    """
    results = []
    for filter_ in filters:
        try:
            # update dynamic path args
            args["path"] = syspath_or_exception(args["fs"], args["fs_path"])
            args["relative_path"] = fspath.frombase(
                args["fs_base_path"], args["fs_path"]
            )

            match, updates = filter_.pipeline(args)
            result = match ^ filter_.inverted
            # we cannot exit early on "any".
            if (filter_mode == "none" and result) or (
                filter_mode == "all" and not result
            ):
                return False
            results.append(result)
            deep_merge_inplace(args, updates)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(e)
            # console.print_exception()
            filter_.print_error(str(e))
            return False

    if filter_mode == "any":
        return any(results)
    return True


def action_pipeline(actions: Iterable[Action], args: dict, simulate: bool) -> bool:
    for action in actions:
        try:
            # update dynamic path args
            args["path"] = syspath_or_exception(args["fs"], args["fs_path"])
            args["relative_path"] = fspath.frombase(
                args["fs_base_path"], args["fs_path"]
            )

            updates = action.pipeline(args, simulate=simulate)
            # jobs may return a dict with updates that should be merged into args
            if updates is not None:
                deep_merge_inplace(args, updates)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(e)
            action.print_error(str(e))
            return False
    return True


def run_rules(rules: dict, simulate: bool = True):
    count = Counter(done=0, fail=0)  # type: Counter

    if simulate:
        console.simulation_banner()

    console.spinner(simulate=simulate)
    for rule_nr, rule in enumerate(rules["rules"], start=1):
        target = rule.get("targets", "files")
        console.rule(rule.get("name", "Rule %s" % rule_nr))
        filter_mode = rule.get("filter_mode", "all")

        for walker, walker_fs, walker_path in rule["locations"]:
            console.location(walker_fs, walker_path)
            walk = walker.files if target == "files" else walker.dirs
            for path in walk(fs=walker_fs, path=walker_path):
                if walker_fs.islink(path):
                    continue
                # tell the user which resource we're handling
                console.path(walker_fs, path)

                # assemble the available args
                args = basic_args()
                args.update(
                    fs=walker_fs,
                    fs_path=path,
                    fs_base_path=walker_path,
                )

                # run resource through the filter pipeline
                match = filter_pipeline(
                    filters=rule["filters"],
                    args=args,
                    filter_mode=filter_mode,
                )

                # if the currently handled resource changed we adjust the prefix message
                if args.get("resource_changed"):
                    console.path_changed_during_pipeline(
                        fs=walker_fs,
                        fs_path=path,
                        new_fs=args["fs"],
                        new_path=args["fs_path"],
                        reason=args.get("resource_changed"),
                    )
                args.pop("resource_changed", None)

                # run resource through the action pipeline
                if match:
                    is_success = action_pipeline(
                        actions=rule["actions"],
                        args=args,
                        simulate=simulate,
                    )
                    if is_success:
                        count["done"] += 1
                    else:
                        count["fail"] += 1

    if simulate:
        console.simulation_banner()

    return count


def run(rules: Union[str, dict], simulate: bool, validate=True):
    # load and validate
    if isinstance(rules, str):
        rules = config.load_from_string(rules)

    rules = config.cleanup(rules)

    migrate_v1(rules)

    if validate:
        config.validate(rules)

    # instantiate
    warnings = replace_with_instances(rules)
    for msg in warnings:
        console.warn(msg)

    # run
    count = run_rules(rules=rules, simulate=simulate)
    console.summary(count)

    if count["fail"]:
        raise RuntimeWarning("Some actions failed.")
