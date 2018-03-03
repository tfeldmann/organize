import pytest
from mock import patch
from organize.utils import Path


@pytest.fixture
def mock_exists():
    with patch.object(Path, 'exists') as mck:
        yield mck


@pytest.fixture
def mock_samefile():
    with patch.object(Path, 'samefile') as mck:
        yield mck


@pytest.fixture
def mock_rename():
    with patch.object(Path, 'rename') as mck:
        yield mck


@pytest.fixture
def mock_move():
    with patch('shutil.move') as mck:
        yield mck


@pytest.fixture
def mock_copy():
    with patch('shutil.copy2') as mck:
        yield mck


@pytest.fixture
def mock_remove():
    with patch('os.remove') as mck:
        yield mck


@pytest.fixture
def mock_trash():
    with patch('send2trash.send2trash') as mck:
        yield mck


@pytest.fixture
def mock_parent():
    with patch.object(Path, 'parent') as mck:
        yield mck


@pytest.fixture
def mock_mkdir():
    with patch.object(Path, 'mkdir') as mck:
        yield mck
