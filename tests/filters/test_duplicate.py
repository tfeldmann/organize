from conftest import make_files, read_files

from organize import core

CONTENT_SMALL = "COPY CONTENT"
CONTENT_LARGE = "XYZ" * 300000

CONFIG_DEEP_DUP_DELETE = """
rules:
  - locations: "."
    subfolders: true
    filters:
      - duplicate:
          detect_original_by: name
    actions:
      - delete
"""


def test_duplicate_smallfiles(testfs):
    files = {
        "unique.txt": "I'm unique.",
        "unique_too.txt": "I'm unique: too.",
        "a.txt": CONTENT_SMALL,
        "copy2.txt": CONTENT_SMALL,
        "other": {
            "copy.txt": CONTENT_SMALL,
            "copy.jpg": CONTENT_SMALL,
            "large.txt": CONTENT_LARGE,
        },
        "large_unique.txt": CONTENT_LARGE,
    }

    make_files(testfs, files)
    core.run(CONFIG_DEEP_DUP_DELETE, simulate=False, working_dir=testfs)
    result = read_files(testfs)
    testfs.tree()
    assert result == {
        "unique.txt": "I'm unique.",
        "unique_too.txt": "I'm unique: too.",
        "a.txt": CONTENT_SMALL,
        "other": {
            "large.txt": CONTENT_LARGE,
        },
    }


def test_duplicate_largefiles(testfs):
    files = {
        "unique.txt": CONTENT_LARGE + "1",
        "unique_too.txt": CONTENT_LARGE + "2",
        "a.txt": CONTENT_LARGE,
        "copy2.txt": CONTENT_LARGE,
        "other": {
            "copy.txt": CONTENT_LARGE,
            "copy.jpg": CONTENT_LARGE,
            "large.txt": CONTENT_LARGE,
        },
    }

    make_files(testfs, files)
    core.run(CONFIG_DEEP_DUP_DELETE, simulate=False, working_dir=testfs)
    result = read_files(testfs)
    testfs.tree()
    assert result == {
        "unique.txt": CONTENT_LARGE + "1",
        "unique_too.txt": CONTENT_LARGE + "2",
        "a.txt": CONTENT_LARGE,
        "other": {},
    }


# TODO detect_original_by: first_seen
# TODO detect_original_by: created
# TODO detect_original_by: lastmodified
