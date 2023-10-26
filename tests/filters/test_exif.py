from pathlib import Path

import pytest
from conftest import ORGANIZE_DIR
from pyfakefs.fake_filesystem import FakeFilesystem

from organize import Config
from organize.filters.exif import matches_tags


@pytest.fixture
def images_folder(fs: FakeFilesystem):
    RESOURCE_DIR = str(ORGANIZE_DIR / "tests" / "resources" / "images-with-exif")
    fs.add_real_directory(
        source_path=RESOURCE_DIR,
        target_path="/resources",
        read_only=True,
    )
    return fs


def test_matches_tags():
    data = {
        "image": {
            "make": "NIKON CORPORATION",
            "model": "NIKON D3200",
        },
        "exif": {
            "flash": "Flash did not fire",
            "saturation": "Normal",
        },
        "gps": {
            "gpsspeed": "0",
        },
    }

    assert matches_tags({"image.make": "NIKON CORPORATION"}, data)
    assert matches_tags({"image.make": "NIKON *"}, data)
    assert not matches_tags({"image.make": "Apple"}, data)
    assert matches_tags({"gps": None}, data)
    assert not matches_tags({"other": None}, data)
    assert matches_tags({"exif.flash": "Flash did not fire"}, data)


def test_exif_read_camera(images_folder):
    config = """
      rules:
        - locations: "/resources"
          filters:
            - name
            - exif:
                image.make: Apple
          actions:
            - write:
                outfile: "/test/out.txt"
                text: '{name}: {exif.image.model}'
                mode: append
    """
    Config.from_string(config).execute(simulate=False)
    out = Path("/test/out.txt").read_text()
    assert "1: DMC-GX80" not in out
    assert "2: NIKON D3200" not in out
    assert "3: iPhone 6s" in out
    assert "4: iPhone 6s" in out
    assert "5: iPhone 5s" in out


def test_exif_filter_by_cam(images_folder):
    config = """
      rules:
        - locations: "/resources"
          filters:
            - name
            - exif:
                image.model: Nikon D3200
          actions:
            - write:
                outfile: "/test/out.txt"
                text: '{name}: {exif.image.model}'
                mode: append
    """
    Config.from_string(config).execute(simulate=False)
    out = Path("/test/out.txt").read_text()
    assert out.strip() == "2: NIKON D3200"


def test_exif_filter_tag_exists_and_date_format(images_folder):
    config = """
      rules:
        - locations: "/resources"
          filters:
            - name
            - exif:
                gps.gpsdate
          actions:
            - write:
                outfile: "/test/out.txt"
                text: '{name}: {exif.gps.gpsdate.strftime("%d.%m.%Y")}'
                mode: append
    """
    Config.from_string(config).execute(simulate=False)
    out = Path("/test/out.txt").read_text()
    assert set(out.splitlines()) == set(
        [
            "3: 12.08.2017",
            "4: 22.02.2018",
            "5: 08.07.2015",
        ]
    )


def test_exif_filter_by_multiple_keys(images_folder):
    config = """
      rules:
        - locations: "/resources"
          filters:
            - name
            - exif:
                image.make: Apple
                exif.lensmodel: "iPhone 6s back camera 4.15mm f/2.2"
          actions:
            - move: "/chosen/"
    """
    Config.from_string(config).execute(simulate=False)
    chosen = set(str(x.name) for x in Path("/chosen").glob("*"))
    assert chosen == set(["3.jpg", "4.jpg"])
