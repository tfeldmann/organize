import os
from pathlib import Path

import pytest

from organize.config import Config
from organize.core import execute_rules

FIXTURE_DIR = Path(__file__).parent.absolute() / "01_basic"


def filenames(files):
    return set([Path(str(f)).name for f in files])


@pytest.mark.datafiles(FIXTURE_DIR)
def test_basic(datafiles):
    os.chdir(datafiles)
    config = Config.from_string(
        """
        rules:
        - folders: '.'
          filters:
            - filename: test
          actions:
            - copy: 'newname.pdf'
        """
    )
    execute_rules(config.rules, simulate=False)
    assert filenames(datafiles.listdir()) == {
        "newname.pdf",
        "newname 2.pdf",
        "newname 3.pdf",
        "test.pdf",
        "asd.txt",
        "config.yaml",
    }


@pytest.mark.datafiles(FIXTURE_DIR)
def test_globstr(datafiles):
    os.chdir(datafiles)
    config = Config.from_string(
        """
        rules:
        - folders: './*.pdf'
          actions:
          - trash
        """
    )
    execute_rules(config.rules, simulate=False)
    assert filenames(datafiles.listdir()) == {"asd.txt", "config.yaml"}
