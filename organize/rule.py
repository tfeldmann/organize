import logging
import re
from copy import deepcopy
from pathlib import Path
from typing import Iterable, Iterator, Text, Tuple, Mapping

import fs
from fs.walk import Walker

from .output import console_output
from .utils import DotDict

WILDCARD_REGEX = re.compile(r"(?<!\\)[\*\?\[]+")
logger = logging.getLogger(__name__)


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


class Rule:
    def __init__(self, folders=None, filters=None, actions=None, config=None):
        self.folders = folders or []
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

    def walker_settings(self, pattern, args) -> Tuple[Text, Mapping]:
        # split path into base path and glob pattern
        folder, glob, recursive = split_glob(pattern)

        # if a recursive glob pattern and not settings are given, adjust max_depth
        if "max_depth" not in args and recursive:
            args["max_depth"] = None

        # combine defaults and folder config
        config = self.config.copy()
        config.update(args)

        walker_conf = dict(
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
        return (folder, walker_conf)

    def walkers(self) -> Iterable[Tuple[Text, Walker]]:
        for entry in self.folders:
            if isinstance(entry, str):
                pattern, args = entry, {}
            else:
                pattern, args = entry
            folder, conf = self.walker_settings(pattern=pattern, args=args)
            walker = Walker(**conf)
            yield (folder, walker)

    def files(self) -> Iterator[Tuple[Text, Text]]:
        for path, walker in self.walkers():
            folder_fs = fs.open_fs(path)
            for f in walker.files(folder_fs):
                yield (path, f)

    def filter_pipeline(self, args: DotDict) -> bool:
        for filter_ in self.filters:
            try:
                result = filter_.pipeline(deepcopy(args))
                if isinstance(result, dict):
                    args.update(result)
                elif not result:
                    # filters might return a simple True / False.
                    # Exit early if a filter does not match.
                    return False
            except Exception as e:  # pylint: disable=broad-except
                logger.exception(e)
                filter_.exception(e)
                return False
        return True

    def action_pipeline(self, args: DotDict) -> bool:
        for action in self.actions:
            try:
                updates = action.pipeline(deepcopy(args))
                # jobs may return a dict with updates that should be merged into args
                if updates is not None:
                    args.update(updates)
            except Exception as e:  # pylint: disable=broad-except
                logger.exception(e)
                action.print_exception(e)
                return False
        return True

    def run_single(self, path, basedir, simulate=True) -> bool:
        # args will be modified in place by action and filter pipeline
        args = DotDict(
            path=Path(fs.path.combine(basedir, path)),
            basedir=Path(basedir),
            relative_path=Path(path),
            simulate=simulate,
        )
        console_output.set_location(args.basedir, args.relative_path)
        match = self.filter_pipeline(args)
        if match:
            return self.action_pipeline(args)

    def run(self, simulate=True):
        if simulate:
            console_output.simulation_banner()

        count = [0, 0]
        for base, path in self.files():
            success = self.run_single(path=path, basedir=base, simulate=simulate)
            if success is not None:
                count[success] += 1
        failed, succeded = count
        if succeded == failed == 0:
            msg = "Nothing to do."
            logger.info(msg)
            print(msg)

        if simulate:
            console_output.simulation_banner()

        return failed > 0


def test():
    from . import actions, filters

    rule = Rule(
        folders=[("~/Documents/", {"max_depth": None}),],
        filters=[filters.Extension("html"),],
        actions=[actions.Echo("{path}")],
    )
    rule.run(simulate=True)


if __name__ == "__main__":
    test()
