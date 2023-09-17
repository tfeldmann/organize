from __future__ import annotations

from dataclasses import dataclass, field
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
