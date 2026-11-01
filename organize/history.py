"""
A journal of the file operations done by `organize run`, so a run can be undone.

Each line in the history file is a JSON object. Operations look like
`{"run": ..., "op": "move", "src": ..., "dst": ...}`, undone runs are marked with
`{"undone": <run id>}`.
"""

import json
import shutil
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterator, List, Literal, Optional

import platformdirs

HISTORY_FILE = platformdirs.user_data_path(appname="organize") / "history.jsonl"

Op = Literal["move", "rename", "copy", "mkdir"]

_current_run: Optional[str] = None


@contextmanager
def recording() -> Iterator[str]:
    """All operations recorded in this context belong to the same run."""
    global _current_run
    prev = _current_run
    _current_run = datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    try:
        yield _current_run
    finally:
        _current_run = prev


def _append(entry: Dict) -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def record(op: Op, dst: Path, src: Optional[Path] = None) -> None:
    if _current_run is None:
        return
    entry = {
        "run": _current_run,
        "time": datetime.now().isoformat(timespec="seconds"),
        "op": op,
        "dst": str(dst),
    }
    if src is not None:
        entry["src"] = str(src)
    _append(entry)


def mkdir(path: Path) -> None:
    """Create a folder with its parents and record which ones are new."""
    missing = [p for p in [path, *path.parents] if not p.exists()]
    path.mkdir(parents=True, exist_ok=True)
    for p in reversed(missing):
        record("mkdir", dst=p)


@dataclass
class Run:
    id: str
    time: str
    ops: List[Dict] = field(default_factory=list)
    undone: bool = False


def runs() -> List[Run]:
    """All recorded runs, oldest first."""
    result: Dict[str, Run] = {}
    if not HISTORY_FILE.exists():
        return []
    with HISTORY_FILE.open(encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if "undone" in entry:
                if entry["undone"] in result:
                    result[entry["undone"]].undone = True
                continue
            run = result.setdefault(entry["run"], Run(entry["run"], entry["time"]))
            run.ops.append(entry)
    return list(result.values())


def last_run() -> Optional[Run]:
    for run in reversed(runs()):
        if not run.undone:
            return run
    return None


def find_run(run_id: str) -> Optional[Run]:
    for run in runs():
        if run.id == run_id:
            return run
    return None


def undo(run: Run, simulate: bool) -> Iterator[str]:
    """Reverts the operations of a run, newest first. Yields a message for each."""
    for op in reversed(run.ops):
        dst = Path(op["dst"])
        if op["op"] in ("move", "rename"):
            src = Path(op["src"])
            if not dst.exists():
                yield f'Skipped "{dst}": it no longer exists'
            elif src.exists():
                yield f'Skipped "{dst}": "{src}" exists again'
            else:
                yield f'Move back "{dst}" -> "{src}"'
                if not simulate:
                    src.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(src=dst, dst=src)
        elif op["op"] == "copy":
            if dst.exists():
                yield f'Trash copy "{dst}"'
                if not simulate:
                    from organize.actions.trash import trash

                    trash(path=dst)
        elif op["op"] == "mkdir":
            if dst.is_dir() and not any(p.name != ".DS_Store" for p in dst.iterdir()):
                yield f'Remove empty folder "{dst}"'
                if not simulate:
                    (dst / ".DS_Store").unlink(missing_ok=True)
                    dst.rmdir()
    if not simulate:
        _append({"undone": run.id})
