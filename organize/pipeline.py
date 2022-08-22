import logging
from pathlib import Path
from typing import List

import fs

from . import console
from .actions import Action
from .filters import Filter
from .utils import deep_merge_inplace
from .rule import FilterMode

logger = logging.getLogger(__name__)


def syspath_or_exception(fs, path):
    try:
        return Path(fs.getsyspath(path))
    except fs.errors.NoSysPath as e:
        return e


def filter_pipeline(filters: List[Filter], args: dict, filter_mode: FilterMode) -> bool:
    """
    run the filter pipeline.
    Returns True on a match, False otherwise and updates `args` in the process.
    """
    results = []
    for filter_ in filters:
        try:
            # update dynamic path args
            args["fs_base_path"] = fs.path.abspath(
                fs.path.normpath(args["fs_base_path"])
            )
            args["fs_path"] = fs.path.abspath(fs.path.normpath(args["fs_path"]))
            args["path"] = syspath_or_exception(args["fs"], args["fs_path"])
            args["relative_path"] = fs.path.frombase(
                args["fs_base_path"], args["fs_path"]
            )

            match, updates = filter_.pipeline(args)
            result = match ^ filter_.filter_is_inverted
            # we cannot exit early on "any".
            if (filter_mode == FilterMode.none and result) or (
                filter_mode == FilterMode.all and not result
            ):
                return False
            results.append(result)
            deep_merge_inplace(args, updates)
        except Exception as e:  # pylint: disable=broad-except
            logger.exception(e)
            console.error(e)
            filter_.print_error(str(e))
            return False

    if filter_mode == "any":
        return any(results)
    return True


def action_pipeline(actions: List[Action], args: dict, simulate: bool) -> bool:
    for action in actions:
        try:
            # update dynamic path args
            args["fs_base_path"] = fs.path.abspath(
                fs.path.normpath(args["fs_base_path"])
            )
            args["fs_path"] = fs.path.abspath(fs.path.normpath(args["fs_path"]))
            args["path"] = syspath_or_exception(args["fs"], args["fs_path"])
            args["relative_path"] = fs.path.frombase(
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
