import os

import pytest
import yaml
from mock import patch

from organize.utils import Path


def pytest_collect_file(parent, path):
    if path.ext == ".yaml" and path.basename.startswith("test"):
        return YamlFile(path, parent)


class YamlFile(pytest.File):
    def collect(self):
        tests = yaml.safe_load_all(self.fspath.open())
        for test in tests:
            yield YamlItem(name=test["description"], parent=self, spec=test)


class YamlItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super().__init__(name, parent)
        self.spec = spec

    def runtest(self):
        if not "config" in self.spec:
            raise YamlException(self, name, value)

    def repr_failure(self, excinfo):
        """ called when self.runtest() raises an exception. """
        if isinstance(excinfo.value, YamlException):
            return "\n".join(
                [
                    "usecase execution failed",
                    "   spec failed: %r: %r" % excinfo.value.args[1:3],
                    "   no further details known at this point.",
                ]
            )

    def reportinfo(self):
        return self.fspath, 0, "usecase: %s" % self.name


class YamlException(Exception):
    """ custom exception for error reporting. """


@pytest.fixture
def mock_exists():
    with patch.object(Path, "exists") as mck:
        yield mck


@pytest.fixture
def mock_samefile():
    with patch.object(Path, "samefile") as mck:
        yield mck


@pytest.fixture
def mock_rename():
    with patch.object(Path, "rename") as mck:
        yield mck


@pytest.fixture
def mock_move():
    with patch("shutil.move") as mck:
        yield mck


@pytest.fixture
def mock_copy():
    with patch("shutil.copy2") as mck:
        yield mck


@pytest.fixture
def mock_remove():
    with patch("os.remove") as mck:
        yield mck


@pytest.fixture
def mock_trash():
    with patch("send2trash.send2trash") as mck:
        yield mck


@pytest.fixture
def mock_parent():
    with patch.object(Path, "parent") as mck:
        yield mck


@pytest.fixture
def mock_mkdir():
    with patch.object(Path, "mkdir") as mck:
        yield mck


def create_filesystem(tmp_path, files):
    for f in files:
        p = tmp_path / Path(f)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()
    os.chdir(str(tmp_path))
