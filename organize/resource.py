from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from organize.utils import deep_merge

if TYPE_CHECKING:
    from .rule import Rule


@dataclass
class Resource:
    """
    A resource is created for each handled file (or folder) and then passed into the
    filters and actions pipeline.

    :param path:
        The path to the current file or folder
    :param basedir:
        The search location as given in rule->location->path
    :param rule:
        The rule which is currently executed
    :param rule_nr:
        The index of the rule in the config file
    :param vars:
        Filters and actions may add values to this dict which are then available for
        other filters and actions in the pipeline.
    :param walker_skip_files:
        Filters and actions may add pathes to this set which are then ignored for the
        rest of the rule.
    """

    path: Optional[Path]
    basedir: Optional[Path] = None
    rule: Optional[Rule] = None  # TODO: not optional?
    rule_nr: int = 0
    vars: Dict[str, Any] = field(default_factory=dict)
    walker_skip_pathes: Set[Path] = field(default_factory=set)

    def relative_path(self) -> Optional[Path]:
        if self.basedir is None:
            return self.path
        if self.path is None:
            return None
        return self.path.relative_to(self.basedir)

    def dict(self):
        return dict(
            path=self.path,
            basedir=self.basedir,
            location=self.basedir,
            relative_path=self.relative_path(),
            rule=self.rule.name if self.rule else None,
            rule_nr=self.rule_nr,
            **self.vars,
        )

    def deep_merge(self, key: str, data: Dict) -> None:
        """
        Convenience method for filters / actions to merge data into the `vars` dict.
        """
        prev = self.vars.get(key, dict())
        self.vars[key] = deep_merge(prev, data)

    # TODO: Caching for `is_file` and `is_dir`
    # TODO: provide a `from_direntry` constructor to speed things up
    def is_file(self) -> bool:
        if self.path is None:
            raise ValueError("No path given")
        return self.path.is_file()

    def is_dir(self) -> bool:
        if self.path is None:
            raise ValueError("No path given")
        return self.path.is_dir()

    def is_empty(self) -> bool:
        if self.path is None:
            raise ValueError("No path given")
        if self.is_file():
            return self.path.stat().st_size == 0
        elif self.is_dir():
            return not any(self.path.iterdir())
        raise ValueError("Unknown file type")
