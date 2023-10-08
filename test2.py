from rich import print

from organize.actions import Echo
from organize.config import Config
from organize.filters import (
    Created,
    DateAdded,
    DateLastUsed,
    Extension,
    Hash,
    LastModified,
    Regex,
    Size,
)
from organize.rule import Rule

rule = Rule(
    locations=["."],
    filter_mode="any",
    filters=[
        Extension(".toml"),
        Hash("sha256"),
        Size(),
        Regex(".*proj"),
        LastModified(),
        Created(),
    ],
    actions=[
        Echo("File {path} has hash {hash}"),
        Echo("{size.traditional}"),
        Echo("{lastmodified}, C: {created}, LU: {date_lastused}"),
    ],
)
conf2 = Config(rules=[rule])
print(conf2)
conf2.execute(simulate=False)
