import pytest
from conftest import ORGANIZE_DIR
from fs import copy

from organize.core import run

RESOURCE_DIR = str(ORGANIZE_DIR / "tests" / "resources" / "images-with-exif")


@pytest.fixture
def images_folder(testfs):
    copy.copy_dir(RESOURCE_DIR, "/", testfs, "/")
    yield testfs


def test_exif_read_camera(images_folder):
    config = """
      rules:
        - locations: "/"
          filters:
            - name
            - exif
          actions:
            - write:
                text: '{name}: {exif.image.model}'
                path: "out.txt"
                mode: append
    """
    run(config, simulate=False, working_dir=images_folder)
    out = images_folder.readtext("out.txt")
    assert "1: DMC-GX80" in out
    assert "2: NIKON D3200" in out
    assert "3: iPhone 6s" in out
    assert "4: iPhone 6s" in out
    assert "5: iPhone 5s" in out


def test_exif_filter_by_cam(images_folder):
    config = """
      rules:
        - locations: "/"
          filters:
            - name
            - exif:
                image.model: Nikon D3200
          actions:
            - write:
                text: '{name}: {exif.image.model}'
                path: "out.txt"
                mode: append
    """
    run(config, simulate=False, working_dir=images_folder)
    out = images_folder.readtext("out.txt")
    assert out.strip() == "2: NIKON D3200"


def test_exif_filter_tag_exists(images_folder):
    config = """
      rules:
        - locations: "/"
          filters:
            - name
            - exif:
                gps.gpsdate
          actions:
            - write:
                text: '{name}: {exif.gps.gpsdate}'
                path: "out.txt"
    """
    run(config, simulate=False, working_dir=images_folder)
    out = images_folder.readtext("out.txt")
    assert len(out.splitlines()) == 3
    assert "4: 2018-02-22" in out
    assert "5: 2015-07-08" in out
    assert "3: 2017-08-12" in out


def test_exif_filter_datetime(images_folder):
    config = """
      rules:
        - locations: "/"
          filters:
            - name
            - exif:
                exif.datetimeoriginal
          actions:
            - write:
                text: "{name}: {exif.exif.datetimeoriginal.isoformat()}"
                path: "out.txt"
    """
    run(config, simulate=False, working_dir=images_folder)
    out = images_folder.readtext("out.txt")
    assert len(out.splitlines()) == 5
    # 1: EXIF DateTimeOriginal 2018:09:29 18:52:46
    assert "1: 2018-09-29T18:52:46" in out
    # 2: EXIF DateTimeOriginal 2018:04:29 16:24:21
    assert "2: 2018-04-29T16:24:21" in out
    # 3: DateTimeOriginal 2017:08:12 12:23:36
    assert "3: 2017-08-12T12:23:36" in out
    # 4: EXIF DateTimeOriginal 2018:02:22 09:34:41
    assert "4: 2018-02-22T09:34:41" in out
    # 5: EXIF DateTimeOriginal 2015:07:08 14:43:52
    assert "5: 2015-07-08T14:43:52" in out


def test_exif_filter_timedelta(images_folder):
    config = """
      rules:
        - locations: "/"
          filters:
            - name
            - exif:
                exif.offsettimeoriginal
          actions:
            - write:
                text: "{name}: {exif.exif.offsettimeoriginal}"
                path: "out.txt"
    """
    run(config, simulate=False, working_dir=images_folder)
    out = images_folder.readtext("out.txt")
    assert len(out.splitlines()) == 1
    # 1: EXIF OffsetTimeOriginal +01:00 -> datetime.timedelta(seconds=3600) -> '1:00:00'
    assert "1: 1:00:00" in out


def test_exif_filter_by_multiple_keys(images_folder):
    config = """
      rules:
        - locations: "/"
          filters:
            - name
            - exif:
                image.make: Apple
                exif.lensmodel: "iPhone 6s back camera 4.15mm f/2.2"
          actions:
            - move: "chosen/"
    """
    run(config, simulate=False, working_dir=images_folder)
    chosen = set(images_folder.listdir("chosen"))
    assert chosen == set(["3.jpg", "4.jpg"])
