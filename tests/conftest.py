from fs.base import FS
from fs.path import join, basename


def make_files(fs: FS, layout: dict, path="/"):
    """
    layout = {
        "folder": {
            "subfolder": {
                "test.txt": "",
                "other.pdf": b"binary",
            },
        },
        "file.txt": "Hello world\nAnother line",
    }
    """
    fs.makedirs(path, recreate=True)
    for k, v in layout.items():
        respath = join(path, k)

        # folders are dicts
        if isinstance(v, dict):
            make_files(fs=fs, layout=v, path=respath)

        # everything else is a file
        elif v is None:
            fs.touch(respath)
        elif isinstance(v, bytes):
            fs.writebytes(respath, v)
        elif isinstance(v, str):
            fs.writetext(respath, v)
        else:
            raise ValueError("Unknown file data %s" % v)


def read_files(fs: FS, path="/"):
    result = dict()
    for x in fs.walk.files(path, max_depth=0):
        result[basename(x)] = fs.readtext(x)
    for x in fs.walk.dirs(path, max_depth=0):
        result[basename(x)] = read_files(fs, path=join(path, x))
    return result
