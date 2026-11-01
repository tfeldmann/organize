from pathlib import Path

import pytest
from conftest import ORGANIZE_DIR

from organize import Config

EXAMPLES = sorted((ORGANIZE_DIR / "examples").glob("*.yaml"))


@pytest.mark.parametrize("path", EXAMPLES, ids=[p.name for p in EXAMPLES])
def test_example_config_is_valid(path: Path):
    Config.from_path(path)
