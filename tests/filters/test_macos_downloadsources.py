import sys

import pytest

from organize import Config
from organize.filters.macos_downloadsource import list_download_urls, match_urls


def test_macos_downloadsource_matching():
    filter_urls = ["https://*.githubusercontent.com/*"]
    assert not match_urls(filter_urls=filter_urls, file_urls=["https://github.com"])
    assert not match_urls(filter_urls=filter_urls, file_urls=None)
    assert match_urls(filter_urls=filter_urls, file_urls=["https://raw.githubusercontent.com/nonexistentlink"])
    assert match_urls(filter_urls=[], file_urls=["https://github.com"])
    assert not match_urls(filter_urls=[], file_urls=None)


@pytest.mark.skipif(sys.platform != "darwin", reason="runs only on macos")
def test_macos_downloadsource_filter(tmp_path, testoutput):
    import osxmetadata


    testdir = tmp_path / "test"
    testdir.mkdir()

    selfmade = testdir / "test.txt"
    selfmade.touch()
    assert list_download_urls(selfmade) is None

    # These tests currently doesn't work as Spotlight does not re-index files in `/tmp` or `/private/var/tmp` when new metadata is set. 

    # example_file = testdir / "example.txt"
    # example_file.touch()
    # osxmetadata.OSXMetaData(example_file).set("kMDItemWhereFroms", ["https://example.com", ""])
    # assert list_download_urls(example_file) == ["https://example.com", ""]

    # Workaround, see below
    from os.path import expanduser
    import random
    import string
    example_file = f"""{expanduser("~")}/{''.join([string.ascii_letters[random.randint(0, len(string.ascii_letters)-1)] for _ in range (20)])}.txt"""
    with open(example_file, 'w') as f:
        f.write("")
    osxmetadata.OSXMetaData(example_file).set("kMDItemWhereFroms", ["https://example.com", ""])
    import time
    time.sleep(3)
    assert list_download_urls(example_file) == ["https://example.com", ""]

    Config.from_string(
            f"""
            rules:
              - locations: ~/
                filters:
                - macos_downloadsource:
                actions:
                - echo: "{{'|<>|'.join(macos_downloadsource)}}"
                - delete
            """
    ).execute(simulate=False, output=testoutput)

    assert testoutput.messages == ["https://example.com|<>|", f"Deleting {example_file}"]
