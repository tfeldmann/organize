from typing import IO
from fs.base import FS
from fs.path import join


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
        elif isinstance(v, IO):
            fs.writefile(respath, v)
        else:
            raise ValueError("Unknown file data %s" % v)


# def assertdir(path, *files):
#     os.chdir(str(path / "files"))
#     assert set(files) == set(str(x) for x in Path(".").glob("**/*") if x.is_file())
