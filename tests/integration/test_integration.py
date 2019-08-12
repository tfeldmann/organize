import os

import pytest
from conftest import create_filesystem

from organize.config import Config
from organize.core import execute_rules
from organize.utils import Path

FIXTURE_DIR = Path(__file__).parent.absolute() / "01_basic"


def filenames(files):
    return set([Path(str(f)).name for f in files])


def test_filename_move(tmp_path):
    create_filesystem(tmp_path, ["sub/test.PY"])
    config = Config.from_string(
        """
        rules:
        - folders: 'sub'
          filters:
          - Extension
          actions:
          - rename: '{path.stem}{path.stem}.{extension.lower}'
        """
    )
    execute_rules(config.rules, simulate=False)
    assert (tmp_path / "sub" / "testtest.py").exists()
    assert not (tmp_path / "sub" / "test.PY").exists()


@pytest.mark.datafiles(FIXTURE_DIR)
def test_basic(datafiles):
    os.chdir(str(datafiles))
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
    os.chdir(str(datafiles))
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
