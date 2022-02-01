from copy import deepcopy
from typing import Any, List, Sequence, Callable

import jinja2
from fs import open_fs, path as fspath
from fs.base import FS
from fs.memoryfs import MemoryFS
from fs.osfs import OSFS
from jinja2 import nativetypes


def finalize_placeholder(x):
    if Callable(x):
        return x()
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


def is_same_resource(fs1, path1, fs2, path2):
    from fs.errors import NoSysPath, NoURL
    from fs.tarfs import ReadTarFS, WriteTarFS
    from fs.zipfs import ReadZipFS, WriteZipFS

    try:
        return fs1.getsyspath(path1) == fs2.getsyspath(path2)
    except NoSysPath:
        pass
    if isinstance(fs1, fs2.__class__):
        try:
            return fs1.geturl(path1) == fs2.geturl(path2)
        except NoURL:
            pass
        if isinstance(fs1, (WriteZipFS, ReadZipFS, WriteTarFS, ReadTarFS)):
            return path1 == path2 and fs1._file == fs2._file
    return False


def resource_description(fs, path):
    if isinstance(fs, SimulationFS):
        return "%s%s" % (str(fs), fspath.abspath(path))
    elif isinstance(fs, OSFS):
        return fs.getsyspath(path)
    elif path == "/":
        return str(fs)
    return "{} on {}".format(path, fs)


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


def deep_merge(a: dict, b: dict) -> dict:
    result = deepcopy(a)
    for bk, bv in b.items():
        av = result.get(bk)
        if isinstance(av, dict) and isinstance(bv, dict):
            result[bk] = deep_merge(av, bv)
        else:
            result[bk] = deepcopy(bv)
    return result


def deep_merge_inplace(base: dict, updates: dict) -> None:
    for bk, bv in updates.items():
        av = base.get(bk)
        if isinstance(av, dict) and isinstance(bv, dict):
            deep_merge_inplace(av, bv)
        else:
            base[bk] = bv


def next_free_name(fs: FS, template: jinja2.Template, name: str, extension: str) -> str:
    """
    Increments {counter} in the template until the given resource does not exist.

    Args:
        fs (FS): the filesystem to work on
        template (jinja2.Template):
            A jinja2 template with placeholders for {name}, {extension} and {counter}
        name (str): The wanted filename
        extension (str): the wanted extension

    Raises:
        ValueError if no free name can be found with the given template.

    Returns:
        (str) A filename according to the given template that does not exist on **fs**.
    """
    counter = 1
    prev_candidate = ""
    while True:
        candidate = template.render(name=name, extension=extension, counter=counter)
        if not fs.exists(candidate):
            return candidate
        if prev_candidate == candidate:
            raise ValueError(
                "Could not find a free filename for the given template. "
                'Maybe you forgot the "{counter}" placeholder?'
            )
        prev_candidate = candidate
        counter += 1
