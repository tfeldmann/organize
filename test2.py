from rich import print

from organize.actions import Echo
from organize.config import Config
from organize.filters import Extension, Hash, LastModified, Regex, Size
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
    ],
    actions=[
        Echo("File {path} has hash {hash}"),
        Echo("{size.traditional}"),
        Echo("{lastmodified}"),
    ],
)
conf2 = Config(rules=[rule])
print(conf2)
conf2.execute(simulate=True)
