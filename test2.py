from pydantic.dataclasses import dataclass
from pydantic import Field, validator


@dataclass
class Foo:
    bar: str = "str"
    qux: int = Field("Test")

    def __post_init__(self):
        self._template = "asd"

    def run(self):
        print(self._template)
        print(self.bar)

    @validator("bar")
    def validate_bar(cls, val):
        print(val)
        return val

print(Foo("asd"))
print(Foo("asd").run())
print(Foo("bar", qux="asd"))
print(Foo("asd", "asd"))
