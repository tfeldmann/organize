import textwrap
from typing import List, Union

import yaml
from fs.base import FS
from pydantic import BaseModel

from . import console
from .pipeline import action_pipeline, filter_pipeline
from .rule import Rule
from .utils import basic_args


def default_yaml_cnst(loader, tag_suffix, node):
    # disable yaml constructors for strings starting with exclamation marks
    # https://stackoverflow.com/a/13281292/300783
    return str(node.tag)


yaml.add_multi_constructor("", default_yaml_cnst, Loader=yaml.SafeLoader)


def load_from_string(config: str) -> dict:
    dedented_config = textwrap.dedent(config)
    return yaml.load(dedented_config, Loader=yaml.SafeLoader)


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


class Config(BaseModel):
    rules: List[Rule]

    class Config:
        title = "organize config file"
        extra = "forbid"
        arbitrary_types_allowed = True

    def execute(
        self,
        simulate: bool = True,
        tags=set(),
        skip_tags=set(),
        working_dir: Union[FS, str] = "",
    ):
        args = basic_args()
        for rule in self.rules:

            # exclude rules by tags
            if not should_execute(rule_tags=rule.tags, tags=tags, skip_tags=skip_tags):
                continue

            for walk_args in rule.walk():
                filesystem = walk_args["fs"]
                fs_path = walk_args["fs_path"]

                console.path(filesystem, fs_path)

                args.update(walk_args)
                match = filter_pipeline(
                    rule.filters, args=args, filter_mode=rule.filter_mode
                )

                if not match:
                    continue

                # # if the currently handled resource changed we adjust the prefix message
                # if args.get("resource_changed"):
                #     console.path_changed_during_pipeline(
                #         fs=filesystem,
                #         fs_path=fs_path,
                #         new_fs=args["fs"],
                #         new_path=args["fs_path"],
                #         reason=args.get("resource_changed"),
                #     )
                # args.pop("resource_changed", None)

                is_success = action_pipeline(
                    actions=rule.actions,
                    args=args,
                    simulate=simulate,
                )


if __name__ == "__main__":
    import sys

    from rich import print

    obj = load_from_string(
        """
        rules:
          - locations: "."
            subfolders: true
            filters:
              - name: "*cache*"
              - extension: json
              - size:
                 - < 1 Mb
                 - < 2MB
            actions:
              - confirm
              - echo: "Test {name} {extension} {size}"
        """
    )
    x = Config.parse_obj(obj)
    print(x)
    x.execute(simulate=True)
    sys.exit()
