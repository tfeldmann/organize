from conftest import make_files, read_files

from organize import Config


def test_mimetype(fs):
    make_files({"test.pdf": "", "other.jpg": ""}, "test")
    Config.from_string(
        """
        rules:
          - locations: /test
            filters:
              - mimetype
            actions:
              - move: /test/{mimetype}/
        """
    ).execute(simulate=False)
    assert read_files("test") == {
        "application": {
            "pdf": {
                "test.pdf": "",
            },
        },
        "image": {
            "jpeg": {
                "other.jpg": "",
            },
        },
    }


def test_mimetype_filter(fs):
    make_files({"test.pdf": "", "other.jpg": "", "other2.png": ""}, "test")
    Config.from_string(
        """
        rules:
          - locations: /test
            filters:
              - mimetype:
                - "image"
            actions:
              - move: /test/{mimetype}/
        """
    ).execute(simulate=False)
    assert read_files("test") == {
        "test.pdf": "",
        "image": {
            "jpeg": {
                "other.jpg": "",
            },
            "png": {
                "other2.png": "",
            },
        },
    }
