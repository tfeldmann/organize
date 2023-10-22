from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from organize.utils import deep_merge

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
            location=self.basedir,
            relative_path=self.relative_path,
            rule=self.rule.name,
            env=os.environ,
            now=datetime.now,
            utcnow=datetime.utcnow,
            today=date.today,
            **self.vars,
        )

    def deep_merge(self, key: str, data: Dict) -> None:
        prev = self.vars.get(key, dict())
        self.vars[key] = deep_merge(prev, data)

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
