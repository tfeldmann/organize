import textwrap
from typing import List, Union

import yaml
from fs.base import FS
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

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


@dataclass(config=ConfigDict(extra="forbid"))
class Config:
    rules: List[Rule]

    @classmethod
    def from_string(cls, config: str):
        dedented = textwrap.dedent(config)
        as_dict = yaml.load(dedented, Loader=yaml.SafeLoader)
        return cls(**as_dict)

    def execute(
        self,
        simulate: bool = True,
        tags=set(),
        skip_tags=set(),
        working_dir: Union[FS, str, None] = ".",
    ):
        for rule in self.rules:
            if should_execute(rule_tags=rule.tags, tags=tags, skip_tags=skip_tags):
                rule.execute(simulate=simulate)


if __name__ == "__main__":
    import sys

    from rich import print

    obj = load_from_string(
        """
        rules:
          - locations: "."
            subfolders: true
            filters:
              - name
            actions:
              - confirm
              - echo: "Test {name} {extension} {size} {hash}"
              - echo: "{mimetype}"
        """
    )
    x = Config.parse_obj(obj)
    print(x.json())
    x.execute(simulate=True)
    sys.exit()
