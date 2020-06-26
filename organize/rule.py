import logging
import re
from copy import deepcopy
from pathlib import Path
from typing import Iterable, Iterator, Text, Tuple, Mapping, Optional

import fs
from fs.walk import Walker
from .glob import Globber
from .output import console_output
from .utils import DotDict

WILDCARD_REGEX = re.compile(r"(?<!\\)[\*\?\[]+")
logger = logging.getLogger(__name__)


class Folder:
    """A Folder object globs a single folder for files or folders
    """

    def __init__(self, path="/", glob="*", *, base_fs="", **kwargs):
        if not base_fs:
            self.base_fs = "osfs://" + path
            self.path = "/"
        else:
            self.base_fs = base_fs
            self.path = path

        self.glob = glob
        self.kwargs = kwargs  # additional walker parameters

    def files(self):
        file_glob = self.glob.rstrip("/")
        for filesystem, path, info in self._glob(file_glob):
            if info.is_file:
                yield filesystem, path

    def dirs(self, **kwargs):
        dir_glob = fs.path.forcedir(self.glob)
        for filesystem, path, info in self._glob(dir_glob):
            if info.is_dir:
                yield filesystem, path

    def _glob(self, pattern):
        with fs.open_fs(self.base_fs) as glob_fs:
            for path, info in Globber(
                fs=glob_fs, pattern=pattern, path=self.path, **self.kwargs
            ):
                yield glob_fs, path, info

    @classmethod
    def from_string(cls, string):
        raise NotImplementedError()  # TODO


class FolderWalker:
    """A FolderWalker globs multiple given folders for files or folders.
    """

    def __init__(self, folders, optimize=True):
        self.folders = folders

    def files(self):
        for folder in self.folders:
            yield from folder.files()

    def dirs(self):
        for folder in self.folders:
            yield from folder.dirs()


"""
Input:
    osfs://~/Documents/
    osfs://~/Pictures
    ! osfs://~/Pictures/Old/*.png
    osfs://~/Pictures/Old/*_include.png
    osfs://~/Pictures/Additional
    osfs://~/Pictures/2020-*/*.png
    osfs://~/Downloads/Folder1/**/*.*
    osfs://~/Downloads/Folder2/**/*


Entrypoints (group by base, then group by path elements):
- osfs://~/Documents/
    - *
- osfs://~/Pictures/
    - /Old/
        - ! *.png
        - *_include.png
    - /Additional/
    - /2020-*/
        - *.png
- osfs://~/Downloads/Folder1
    - **/*.*
- osfs://~/Downloads/Folder2
    - **/*
"""


def create_file_glob(pattern: Text) -> Tuple[Text, Text]:
    # If the glob pattern ends in a /, it will only match directory paths, otherwise it
    # will match files and directories.
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

    return (url + fs.path.join(*base), fs.path.join(*glob))


class Rule:
    def __init__(self, folders=None, filters=None, actions=None, **kwargs):
        self.folders = folders or []
        self.filters = filters or []
        self.actions = actions or []

        self.config = {
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
            # TODO: "group_by_folder": False,  - only possible in RuleGrouper
            # TODO: "normalize_unicode": True,
            # TODO: "case_sensitive": True,
        }
        self.config.update(kwargs)

    def walker_settings(self, pattern, args) -> Tuple[Text, Mapping]:
        parsed_pattern = parse_pattern(pattern)  # type: Pattern

        # if a recursive glob pattern and not settings are given, adjust max_depth
        if "max_depth" not in args:
            args["max_depth"] = parsed_pattern.max_depth

        # combine defaults and folder config
        config = self.config.copy()
        config.update(args)

        walker_conf = dict(
            filter=parsed_pattern.glob_files,
            filter_dirs=parsed_pattern.glob_dirs,
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
        return (parsed_pattern.base, walker_conf)

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

    def run_single(self, path, basedir, simulate=True) -> Optional[bool]:
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
        return None

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
        folders=[Folder(path="~/Documents", glob="**/*")],
        filters=[filters.Extension("pdf"),],
        actions=[actions.Echo("{path}")],
    )
    rule.run(simulate=True)


if __name__ == "__main__":
    test()
