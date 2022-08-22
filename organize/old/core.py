import logging
from collections import Counter
from copy import copy
from pathlib import Path
from typing import Iterable, NamedTuple, Union

import fs
from fs import path as fspath
from fs.base import FS
from fs.errors import NoSysPath, ResourceNotFound
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


def run_rules(rules: dict, tags, skip_tags, simulate: bool = True):
    count = Counter(done=0, fail=0)  # type: Counter

    if simulate:
        console.simulation_banner()

    console.spinner(simulate=simulate)
    for rule_nr, rule in enumerate(rules["rules"], start=1):
        rule_tags = rule.get("tags")
        if isinstance(rule_tags, str):
            rule_tags = [tag.strip() for tag in rule_tags.split(",")]
        should_run = should_execute(
            rule_tags=rule_tags,
            tags=tags,
            skip_tags=skip_tags,
        )
        if not should_run:
            continue
        target = rule.get("targets", "files")
        console.rule(rule.get("name", "Rule %s" % rule_nr))
        filter_mode = rule.get("filter_mode", "all")

        for walker, walker_fs, walker_path in rule["locations"]:
            console.location(walker_fs, walker_path)
            walk = walker.files if target == "files" else walker.dirs
            for path in walk(fs=walker_fs, path=walker_path):
                try:
                    if walker_fs.islink(path):
                        continue
                except ResourceNotFound:
                    console.warn(
                        "Ignoring "
                        + walker_fs.getsyspath(path)
                        + " (may be a broken symlink)"
                    )
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


def run(
    rules: Union[str, dict],
    simulate: bool,
    working_dir: Union[FS, str] = ".",
    validate=True,
    tags=None,
    skip_tags=None,
):
    # load and validate
    if isinstance(rules, str):
        rules = config.load_from_string(rules)

    rules = config.cleanup(rules)
    Action.Meta.default_filesystem = working_dir

    migrate_v1(rules)

    if validate:
        config.validate(rules)

    # instantiate
    warnings = replace_with_instances(rules, default_filesystem=working_dir)
    for msg in warnings:
        console.warn(msg)

    # run
    count = run_rules(rules=rules, tags=tags, skip_tags=skip_tags, simulate=simulate)
    console.summary(count)

    if count["fail"]:
        raise RuntimeWarning("Some actions failed.")
