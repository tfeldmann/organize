import re
import os
from copy import deepcopy
from datetime import datetime
from typing import Any, List, Sequence, Tuple, Union

import jinja2
from fs import open_fs
from fs import path as fspath
from fs.base import FS
from fs.memoryfs import MemoryFS
from jinja2 import nativetypes


def finalize_placeholder(x):
    # This is used to make the `path` arg available in the filters and actions.
    # If a template uses `path` where no syspath is available this makes it possible
    # to raise an exception.
    if isinstance(x, Exception):
        raise x
    return x


Template = jinja2.Environment(
    variable_start_string="{",
    variable_end_string="}",
    autoescape=False,
    finalize=finalize_placeholder,
)

NativeTemplate = nativetypes.NativeEnvironment(
    variable_start_string="{",
    variable_end_string="}",
    autoescape=False,
    finalize=finalize_placeholder,
)


def basic_args():
    """The basic args which are guaranteed to be available."""
    return {
        "env": os.environ,
        "now": datetime.now(),
        "utcnow": datetime.utcnow(),
    }


class SimulationFS(MemoryFS):
    def __init__(self, fs_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fs_url = fs_url

    def __str__(self):
        if not self.fs_url:
            return "<Simulation>"
        elif "://" in self.fs_url:
            return "<%s>" % self.fs_url
        return self.fs_url


def open_fs_or_sim(fs_url, *args, simulate=False, **kwargs):
    if simulate:
        simFS = SimulationFS(fs_url)
        return simFS
    return open_fs(fs_url, *args, **kwargs)


def isabsolute(path):
    """path starts with / or a drive letter"""
    return path.startswith("/") or re.match(r"[a-zA-Z]:[\\/]", path)


def resolve_fs_path(
    filesystem: Union[FS, str, None],
    path: str,
    working_dir: Union[FS, str, None],
) -> Tuple[Union[FS, str], str]:
    """
    use in this order as filesystem:
        filesystem (if given)
        working_dir (if FS or FS_URL)
        path (if absolute as osfs)
        working_dir
    """
    if filesystem:
        return filesystem, path
    if isinstance(working_dir, FS) or (
        isinstance(working_dir, str) and "://" in working_dir
    ):
        return working_dir, path
    if isabsolute(path):
        return path, ""
    return working_dir, path


def expand_user(fs_url: str) -> str:
    fs_url = os.path.expanduser(fs_url)
    if fs_url.startswith("zip://~"):
        fs_url = fs_url.replace("zip://~", "zip://" + os.path.expanduser("~"))
    elif fs_url.startswith("tar://~"):
        fs_url = fs_url.replace("tar://~", "tar://" + os.path.expanduser("~"))
    return fs_url


def expand_args(template: Union[str, jinja2.environment.Template], args=None):
    _args = deep_merge(basic_args(), args or {})
    if isinstance(template, str):
        text = Template.from_string(template).render(**_args)
    else:
        text = template.render(**_args)

    # expand user and fill environment vars
    text = expand_user(text)
    text = os.path.expandvars(text)
    return text


def fs_path_expand(filesystem, path, working_dir, args=None):
    """returns a tuple (fs, path)"""
    # expand args
    path = expand_args(path, args=args)
    if isinstance(filesystem, str):
        filesystem = expand_args(filesystem, args=args)
    if isinstance(working_dir, str):
        working_dir = expand_args(working_dir, args=args)

    result = resolve_fs_path(filesystem=filesystem, path=path, working_dir=working_dir)

    print("resolved (%s, %s, %s) -> %s" % (filesystem, path, working_dir, result))
    return result


def fs_path_from_options(
    path: str, filesystem: Union[FS, str, None] = ""
) -> Tuple[FS, str]:
    """
    path can be a fs_url a normal fs_path
    filesystem is optional and may be a fs_url.

    - user tilde is expanded
    - if a filesystem is given, we use that.
    - otherwise we treat the path as a filesystem.
    """
    path = expand_args(path)

    if filesystem:
        if isinstance(filesystem, str):
            filesystem = expand_args(filesystem)
            return (open_fs(filesystem), path)  # type: ignore
        return (filesystem, path)
    return (open_fs(path), "/")


def unwrap_wrapfs(fs, path):
    from fs.path import abspath
    from fs.wrapfs import WrapFS

    if isinstance(fs, WrapFS):
        fs, path = fs.delegate_path(path)
    return fs, abspath(path)


def is_same_resource(fs1: FS, path1: str, fs2: FS, path2: str):
    from fs.errors import NoSysPath, NoURL

    # obvious check
    if fs1 == fs2 and path1 == path2:
        return True

    # check all fs with syspath support
    try:
        return fs1.getsyspath(path1) == fs2.getsyspath(path2)
    except NoSysPath:
        pass

    # check all fs with url support
    if isinstance(fs1, fs2.__class__):
        try:
            return fs1.geturl(path1) == fs2.geturl(path2)
        except NoURL:
            pass
    return False


def safe_description(fs: FS, path):
    try:
        if isinstance(fs, SimulationFS):
            return "%s%s" % (str(fs), fspath.abspath(path))
        return fs.getsyspath(path)
    except Exception as e:
        return '{} in "{}"'.format(path, fs)


def ensure_list(inp):
    if not isinstance(inp, list):
        return [inp]
    return inp


def ensure_dict(inp):
    if isinstance(inp, dict):
        return inp
    elif isinstance(inp, str):
        return {inp: {}}
    raise ValueError("Cannot ensure dict: %s" % inp)


def to_args(inp):
    """Convert a argument into a (args, kwargs) tuple.

    >>> to_args(None)
    ([], {})
    >>> to_args('test')
    (['test'], {})
    >>> to_args([1, 2, 3])
    ([1, 2, 3], {})
    >>> to_args({'a': {'b': 'c'}})
    ([], {'a': {'b': 'c'}})
    >>> to_args([[1, 2, [3, 4], [5, 6]]])
    ([1, 2, 3, 4, 5, 6], {})
    """
    if inp is None:
        return ([], {})
    if isinstance(inp, dict):
        return ([], inp)
    return (flatten(ensure_list(inp)), {})


def flatten(arr: List[Any]) -> List[Any]:
    if arr == []:
        return []
    if not isinstance(arr, list):
        return [arr]
    return flatten(arr[0]) + flatten(arr[1:])


def flattened_string_list(x, case_sensitive=True) -> Sequence[str]:
    x = [str(x) for x in flatten(x)]
    if not case_sensitive:
        x = [x.lower() for x in x]
    return x


def flatten_all_lists_in_dict(obj):
    """
    >>> flatten_all_lists_in_dict({1: [[2], [3, {5: [5, 6]}]]})
    {1: [2, 3, {5: [5, 6]}]}
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = flatten_all_lists_in_dict(value)
        return obj
    elif isinstance(obj, list):
        return [flatten_all_lists_in_dict(x) for x in flatten(obj)]
    else:
        return obj


def deep_merge(a: dict, b: dict, *, add_keys=True) -> dict:
    result = deepcopy(a)
    for bk, bv in b.items():
        av = result.get(bk)
        if isinstance(av, dict) and isinstance(bv, dict):
            result[bk] = deep_merge(av, bv, add_keys=add_keys)
        elif (av is not None) or add_keys:
            result[bk] = deepcopy(bv)
    return result


def deep_merge_inplace(base: dict, updates: dict) -> None:
    for bk, bv in updates.items():
        av = base.get(bk)
        if isinstance(av, dict) and isinstance(bv, dict):
            deep_merge_inplace(av, bv)
        else:
            base[bk] = bv
