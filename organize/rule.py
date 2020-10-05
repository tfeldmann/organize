"""
https://github.com/tfeldmann/organize/pull/85
"""
import logging
import re
from collections import namedtuple
from copy import deepcopy
from os.path import abspath, expanduser, expandvars
from pathlib import Path
from typing import Optional

import fs

from .glob import Globber
from .output import console_output
from .utils import DotDict

WILDCARD_REGEX = re.compile(r"(?<!\\)[\*\?\[]+")
logger = logging.getLogger(__name__)

GlobItem = namedtuple("GlobItem", "label base_fs base_dir path")

DEFAULT_OPTIONS = {
    "exclude_dirnames": (),
    "exclude_filenames": (),
    "system_exclude_dirnames": ("*.git", "*.svn", ".venv", ".pio"),
    "system_exclude_filenames": (
        "thumbs.db",
        "desktop.ini",
        "~$*",
        ".DS_Store",
        ".localized",
    ),
    "max_depth": 0,
    "search": "breadth",
    "ignore_errors": False,
    "case_sensitive": True,
    "namespaces": "basic",
    "expanduser": True,
    "expandvars": True,
    # TODO:
    "group_by_folder": False,
    "normalize_unicode": True,
    "skip_handled_files": True,
}


def merge_options(options, defaults):
    result = defaults.copy()
    if options:
        result.update(options)
    return result


class Folder:
    """A Folder object globs a single folder for files or folders"""

    def __init__(
        self, path="/", glob="*", *, base_fs="osfs:///", options=None, defaults=None
    ):
        self.base_dir = str(path)
        self.glob = glob
        self.base_fs = base_fs

        self._options = options or {}
        self.defaults = defaults or DEFAULT_OPTIONS

    def label(self):
        if self.base_fs.startswith("osfs://"):
            return self.base_dir
        else:
            return self.base_fs + self.base_dir if self.base_dir != "/" else ""

    def _glob(self, pattern):
        """ execute the given glob pattern """
        options = merge_options(self._options, self.defaults)

        path = self.base_dir
        if options["expanduser"]:
            path = expanduser(path)
        if options["expandvars"]:
            path = expandvars(path)
        path = abspath(path)

        globber_kwargs = dict(
            pattern=pattern,
            path=path,
            max_depth=options["max_depth"],
            case_sensitive=options["case_sensitive"],
            exclude_dirs=(
                options["exclude_dirnames"] + options["system_exclude_dirnames"]
            ),
            exclude_files=(
                options["exclude_filenames"] + options["system_exclude_filenames"]
            ),
            search=options["search"],
            ignore_errors=options["ignore_errors"],
            namespaces=options["namespaces"],
        )
        with fs.open_fs(self.base_fs) as glob_fs:
            for path, info in Globber(fs=glob_fs, **globber_kwargs):
                yield glob_fs, path, info

    def files(self):
        label = self.label()
        file_glob = self.glob.rstrip("/")
        for filesystem, path, info in self._glob(pattern=file_glob):
            if info.is_file:
                yield GlobItem(
                    label=label,
                    base_fs=filesystem,
                    base_dir=self.base_dir,
                    path=path,
                )

    def dirs(self, **kwargs):
        label = self.label()
        dir_glob = fs.path.forcedir(self.glob)
        for filesystem, path, info in self._glob(pattern=dir_glob):
            if info.is_dir:
                yield GlobItem(
                    label=label,
                    base_fs=filesystem,
                    base_dir=self.base_dir,
                    path=path,
                )

    @classmethod
    def from_string(cls, pattern: str) -> "Folder":
        """
        Allowed pattern formats:
            - zip://./Archiv.zip/test/**/test.*
            - Office/2019/
            - Office/201*/*

        returns:
            A `Folder` instance.
        """
        # TODO: base_fs detection for zip files.
        # If the glob pattern ends in a /, it will only match directory paths, otherwise
        # it will match files and directories.
        url = ""
        index = pattern.find("://")  # find filesystem urls
        if index > 0:
            url, pattern = pattern[: index + 3], pattern[index + 3 :]
        base, glob = [], []
        force_glob = False
        for component in fs.path.iteratepath(pattern):
            if force_glob or WILDCARD_REGEX.search(component):
                glob.append(component)
                force_glob = True
            else:
                base.append(component)
        return cls(path=(url + fs.path.join(*base)), glob=fs.path.join(*glob))


class Rule:
    def __init__(
        self, folders=None, filters=None, actions=None, options=None, defaults=None
    ):
        self.folders = folders or []
        self.filters = filters or []
        self.actions = actions or []
        self._options = options or {}
        self.defaults = defaults or DEFAULT_OPTIONS

    def options(self):
        return merge_options(self._options, self.defaults)

    def files(self):
        options = self.options()
        for folder in self.folders:
            folder.defaults = options
            yield from folder.files()

    def dirs(self):
        options = self.options()
        for folder in self.folders:
            folder.defaults = options
            yield from folder.dirs()

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

    def pipeline(self, item: GlobItem, simulate=True) -> Optional[bool]:
        # args will be modified in place by action and filter pipeline
        args = DotDict(
            basedir=item.base_dir,
            path=Path(fs.path.combine(item.base_dir, item.path)),
            relative_path=Path(fs.path.relativefrom(item.base_dir, item.path)),
            simulate=simulate,
        )
        console_output.set_location(item.label, args.relative_path)
        match = self.filter_pipeline(args)
        if match:
            return self.action_pipeline(args)
        return None

    def run(self, simulate=False):
        if simulate:
            console_output.simulation_banner()

        count = [0, 0]
        for item in self.files():
            success = self.pipeline(item=item, simulate=simulate)
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

    def sim(self):
        self.run(simulate=True)


class RuleBook:
    def __init__(self, rules=None, options=None, defaults=None):
        self.rules = rules or []
        self._options = options or {}
        self.defaults = defaults or DEFAULT_OPTIONS

    def run(self, simulate=False):
        options = merge_options(self._options, self.defaults)
        for rule in self.rules:
            rule.defaults = options
            rule.run(simulate=simulate)

    def sim(self):
        self.run(simulate=True)


def test():
    from . import actions, filters

    book = RuleBook(
        [
            Rule(
                folders=[
                    Folder(
                        path="~/Desktop",
                        glob="**/*",
                    ),
                    Folder(
                        base_fs="zip://testzip.zip",
                        path="/",
                        glob="**/*",
                    ),
                ],
                filters=[filters.Extension()],
                actions=[actions.Echo("{extension.upper}")],
            )
        ],
        options={"max_depth": 1},
    )
    book.sim()


if __name__ == "__main__":
    test()
