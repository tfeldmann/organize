"""
Machine readable helpers for front ends like the macOS menu bar app.
"""

import shutil
from pathlib import Path
from typing import Any, Dict, List

from organize import history
from organize.actions.common.conflict import next_free_name
from organize.config import Config
from organize.filters.ai import AI
from organize.template import Template
from organize.watch import watched_folders


def info(config: Config) -> Dict[str, Any]:
    """The folders a config sorts and the categories its AI filters use."""
    categories: List[str] = []
    review: List[str] = []
    for rule in config.rules:
        for flt in rule.filters:
            if isinstance(flt, AI):
                for name in flt.categories:
                    if name not in categories:
                        categories.append(name)
                if flt.uncertain not in review:
                    review.append(flt.uncertain)
    return {
        "folders": [str(f) for f in watched_folders(config)],
        "categories": categories,
        "review_folders": review,
        "history_file": str(history.HISTORY_FILE),
    }


def move(src: Path, dest_dir: Path) -> Path:
    """
    Moves `src` into `dest_dir` (created if needed) as its own undoable run.
    An existing file of the same name is kept and the moved one renamed.
    """
    src = src.resolve(strict=True)
    dest_dir = dest_dir.expanduser().resolve()
    dst = dest_dir / src.name
    if dst == src:
        return src
    with history.recording():
        history.mkdir(dest_dir)
        if dst.exists():
            dst = next_free_name(
                dst=dst, template=Template.from_string("{name} {counter}{extension}")
            )
        shutil.move(src=src, dst=dst)
        history.record("move", src=src, dst=dst)
    return dst
