import os
import shutil

from conftest import TESTS_FOLDER, assertdir, create_filesystem

from organize.cli import main


def copy_resources(tmp_path):
    src = os.path.join(TESTS_FOLDER, "resources")
    dst = os.path.join(str(tmp_path), "files")
    shutil.copytree(src=src, dst=dst)


def test_exif(tmp_path):
    """Sort photos by camera"""
    copy_resources(tmp_path)
    create_filesystem(
        tmp_path,
        files=["nothing.jpg"],
        config="""
        rules:
        - folders: files
          filters:
            - extension: jpg
            - exif
          actions:
            - move: 'files/{exif.image.model}/'
            - echo: "{exif}"
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


def test_exif_filter_single(tmp_path):
    """Filter by camera"""
    copy_resources(tmp_path)
    create_filesystem(
        tmp_path,
        files=["nothing.jpg"],
        config="""
        rules:
        - folders: files
          filters:
            - exif:
                image.model: Nikon D3200
          actions:
            - move: 'files/{exif.image.model}/'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path,
        "nothing.jpg",
        "1.jpg",
        "NIKON D3200/2.jpg",
        "3.jpg",
        "4.jpg",
        "5.jpg",
    )


def test_exif_filter_tag_exists(tmp_path):
    """Filter by GPS"""
    copy_resources(tmp_path)
    create_filesystem(
        tmp_path,
        files=["nothing.jpg"],
        config="""
        rules:
        - folders: files
          filters:
            - exif:
               gps.gpsdate
          actions:
            - echo: "{exif.gps.gpsdate}"
            - move: 'files/has_gps/'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path,
        "nothing.jpg",
        "1.jpg",
        "2.jpg",
        "has_gps/3.jpg",
        "has_gps/4.jpg",
        "has_gps/5.jpg",
    )


def test_exif_filter_multiple(tmp_path):
    """Filter by camera"""
    copy_resources(tmp_path)
    create_filesystem(
        tmp_path,
        files=["nothing.jpg"],
        config="""
        rules:
        - folders: files
          filters:
            - exif:
                image.make: Apple
                exif.lensmodel: "iPhone 6s back camera 4.15mm f/2.2"
          actions:
            - echo: "{exif.image}"
            - move: 'files/chosen/'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    assertdir(
        tmp_path,
        "nothing.jpg",
        "1.jpg",
        "2.jpg",
        "chosen/3.jpg",
        "chosen/4.jpg",
        "5.jpg",
    )
