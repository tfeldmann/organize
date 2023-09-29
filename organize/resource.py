from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .rule import Rule


@dataclass
class Resource:
    path: Path
    basedir: Optional[Path] = None
    rule: Optional[Rule] = None
    vars: Dict[str, Any] = field(default_factory=dict)

    def relative_path(self):
        return self.path.relative_to(self.basedir)

    def dict(self):
        return dict(
            path=self.path,
            basedir=self.basedir,
            relative_path=self.relative_path,
            rule=self.rule.name,
            env=os.environ,
            now=datetime.now,
            utcnow=datetime.utcnow,
            today=date.today,
            **self.vars,
        )

    # TODO: Caching for `is_file` and `is_dir`
    # TODO: provide a `from_direntry` constructor to speed things up
    def is_file(self):
        return self.path.is_file()

    def is_dir(self):
        return self.path.is_dir()

    def is_empty(self):
        if self.is_file():
            return self.path.stat().st_size == 0
        elif self.is_dir():
            return not any(self.path.iterdir())
        raise ValueError("Unknown file type")

    def hash(self, algo: str, *, _bufsize=2**18):
        h = hashlib.new(algo)
        buf = bytearray(_bufsize)
        view = memoryview(buf)
        with open(self.path, "rb", buffering=0) as f:
            while size := f.readinto(view):
                h.update(view[:size])
        return h.hexdigest()

    def size(self):
        if self.is_file():
            return self.path.stat().st_size
        if self.is_dir():
            return sum(f.stat().st_size for f in self.path.glob("**/*") if f.is_file())
