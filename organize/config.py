from __future__ import annotations

import textwrap
from pathlib import Path
from typing import List, Optional, Union

import yaml
from pydantic import ConfigDict, ValidationError
from pydantic.dataclasses import dataclass

from organize.output import Default as RichOutput
from organize.output import Output

from .errors import ConfigError
from .rule import Rule


def default_yaml_cnst(loader, tag_suffix, node):
    # disable yaml constructors for strings starting with exclamation marks
    # https://stackoverflow.com/a/13281292/300783
    return str(node.tag)


yaml.add_multi_constructor("", default_yaml_cnst, Loader=yaml.SafeLoader)


def should_execute(rule_tags, tags, skip_tags):
    """
    returns whether the rule with `rule_tags` should be executed,
    given `tags` and `skip_tags`
    """
    if not rule_tags:
        rule_tags = set()
    if not tags:
        tags = set()
    if not skip_tags:
        skip_tags = set()

    if "always" in rule_tags and "always" not in skip_tags:
        return True
    if "never" in rule_tags and "never" not in tags:
        return False
    if not tags and not skip_tags:
        return True
    if not rule_tags and tags:
        return False
    should_run = any(tag in tags for tag in rule_tags) or not tags or not rule_tags
    should_skip = any(tag in skip_tags for tag in rule_tags)
    return should_run and not should_skip


@dataclass(config=ConfigDict(extra="ignore"))
class Config:
    rules: List[Rule]

    _config_path: Optional[Path] = None

    @classmethod
    def from_string(cls, config: str, config_path: Optional[Path] = None):
        dedented = textwrap.dedent(config)
        as_dict = yaml.load(dedented, Loader=yaml.SafeLoader)
        try:
            return cls(**as_dict)
        except ValidationError as e:
            # add a config_path property to the ValidationError
            raise ConfigError(e=e, config_path=config_path) from e

    @classmethod
    def from_path(cls, config_path: Path):
        inst = cls.from_string(config_path.read_text(), config_path=config_path)
        inst._config_path = config_path
        return inst

    def execute(
        self,
        simulate: bool = True,
        output: Output = RichOutput(),
        tags=set(),
        skip_tags=set(),
        working_dir: Union[str, None] = ".",
    ):
        output.start(simulate=simulate, config_path=self._config_path)
        try:
            for rule_nr, rule in enumerate(self.rules):
                if should_execute(
                    rule_tags=rule.tags,
                    tags=tags,
                    skip_tags=skip_tags,
                ):
                    rule.execute(
                        simulate=simulate,
                        output=output,
                        rule_nr=rule_nr,
                    )
        finally:
            output.end(0, 0)
