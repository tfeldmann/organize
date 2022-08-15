from typing import Dict, Union

from fs import errors
from fs.base import FS
from fs.opener import open_fs
from fs.opener.errors import OpenerError
from fs.path import basename, dirname

from organize.utils import SimulationFS, expand_args


def open_create_fs_path(fs: Union[str, FS], path: str, args: Dict, simulate: bool):
    if fs:
        if isinstance(fs, str):
            dst_fs = expand_args(fs, args)
        else:
            dst_fs = fs
    else:
        dst_fs = dirname(path)
    dst_path = basename(path)
    try:
        dst_fs = open_fs(dst_fs, create=False, writeable=True)
    except (errors.CreateFailed, OpenerError):
        if not simulate:
            dst_fs = open_fs(dst_fs, create=True, writeable=True)
        else:
            dst_fs = SimulationFS(dst_fs)
    return dst_fs, dst_path
