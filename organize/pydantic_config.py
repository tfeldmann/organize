import yaml
import textwrap
from typing import List

from pydantic import BaseModel

from .rule import Rule


class Config(BaseModel):
    rules: List[Rule]

    class Config:
        title = "organize config file"


def default_yaml_cnst(loader, tag_suffix, node):
    # disable yaml constructors for strings starting with exclamation marks
    # https://stackoverflow.com/a/13281292/300783
    return str(node.tag)


yaml.add_multi_constructor("", default_yaml_cnst, Loader=yaml.SafeLoader)


def load_from_string(config: str) -> dict:
    dedented_config = textwrap.dedent(config)
    return yaml.load(dedented_config, Loader=yaml.SafeLoader)


if __name__ == "__main__":
    import sys
    from rich import print

    obj = load_from_string(
        """
        rules:
          - locations:
              - path: "."
            subfolders: true
            actions:
              - move: "somewhere"
        """
    )
    x = Config.parse_obj(obj)
    print(x)

    from .location import Location
    from .pydantic_actions import Move

    print(
        Rule(
            locations=Location(path="asd", exclude_dirs="asd"),
            actions=[Move(dest="asd"), {"move": "test"}],
            filters=[],
            targets="dirs",
        ).dict()
    )
    sys.exit()
