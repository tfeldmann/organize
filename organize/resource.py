from __future__ import annotations

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

    @property
    def relative_path(self):
        return self.path.relative_to(self.basedir)

    @property
    def env(self):
        return os.environ

    @property
    def now(self):
        return datetime.now()

    @property
    def utcnow(self):
        return datetime.utcnow()

    @property
    def today(self):
        return date.today()

    def is_dir(self):
        return self.path.is_dir()
