from enum import Enum
from itertools import count
from pathlib import Path
from typing import Any, List

from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from rich import print

from organize.filter import Not
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


@dataclass
class Extension:
    extensions: str = ""

    def pipeline(self, res: Resource) -> dict:
        res.vars["extension"] = "my-extension"
        return res.path.endswith("pdf")


register_filter(Extension, "extension")
register_action(Echo, "echo")


class Config(BaseModel, extra="forbid"):
    rules: List[Rule]

    def execute(self, simulate: bool):
        rule_count = count(start=1)
        for rule in self.rules:
            rule.execute(simulate=simulate)


# config = {
#     "rules": [
#         {
#             "enabled": True,
#             "locations": [
#                 {
#                     "path": "~/Test",
#                 }
#             ],
#             "subfolders": True,
#             "filters": [
#                 "extension",
#                 {
#                     "not extension": ".pdf",
#                 },
#                 {
#                     "extension": {
#                         "extensions": ".txt",
#                     },
#                 },
#             ],
#             "actions": ["echo"],
#         }
#     ]
# }

# conf = Config.model_validate(config)
# print(conf)

rule = Rule(
    locations=["."],
    subfolders=True,
    filters=[
        Extension(".pdf"),
        #        Not(Extension(".txt")),
    ],
    actions=[Echo("test")],
)
conf2 = Config(rules=[rule])
print(conf2)
conf2.execute(simulate=True)
