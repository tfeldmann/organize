import os
import shutil

from conftest import TESTS_FOLDER, create_filesystem, assertdir
from organize.cli import main


def copy_resources(tmp_path):
    shutil.copytree(src=os.path.join(TESTS_FOLDER, "resources"), dst=tmp_path / "files")


def test_exif(tmp_path):
    """ Sort photos by camera """
    copy_resources(tmp_path)
    create_filesystem(
        tmp_path,
        files=["nothing.jpg"],
        config="""
        rules:
        - folders: files
          filters:
            - exif
          actions:
            - move: 'files/{exif.image.model}/'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path,
        "nothing.jpg",
        "DMC-GX80/1.jpg",
        "NIKON D3200/2.jpg",
        "iPhone 6s/3.jpg",
        "iPhone 6s/4.jpg",
        "iPhone 5s/5.jpg",
    )
