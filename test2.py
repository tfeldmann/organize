from typing import List

from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from rich import print

from organize.config import Config
from organize.filter import Not, Or
from organize.filters.extension import Extension
from organize.output import Output
from organize.registry import register_action, register_filter
from organize.resource import Resource
from organize.rule import Rule


@dataclass
class Echo:
    msg: str = ""

    def pipeline(self, res: Resource, output: Output, simulate: bool) -> dict:
        output.info(res=res, msg=self.msg)
        return res


register_filter(Extension, "extension")
register_action(Echo, "echo")

rule = Rule(
    locations=["."],
    subfolders=True,
    filters=[
        Or(Extension(".toml"), Extension(".pdf")),
    ],
    actions=[Echo("test")],
)
conf2 = Config(rules=[rule])
print(conf2)
conf2.execute(simulate=True)


print(
    Config.from_string(
        """
        rules:
            - locations: "."
              actions:
                - echo: "test"
        """
    )
)
