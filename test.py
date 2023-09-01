from typing import Union, List
from pathlib import Path
from pydantic import BaseModel


class Move:
    def __init__(self, dest: Path = Path(".")):
        self.dest = dest

    def __str__(self):
        return f'<Move(dest="{self.dest}")>'


class MoveSchemaArgs(BaseModel):
    dest: Path


class MoveSchema(BaseModel):
    move: Union[Path, MoveSchemaArgs]
    
    def to_model(self):
        if isinstance(self.move, BaseModel):
            return Move(**self.move.dict())
        elif self.move is None:
            return Move()
        return Move(self.move)


class ExtensionSchema(BaseModel):
    extension: str | None

class RuleSchema(BaseModel):
    actions: List[MoveSchema]
    filters: List[ExtensionSchema]

config = {
    "actions": [
        {"move": "."},
        {"move": {"dest": "/test/test"}},
    ],
    "filters": [
        {"extension": None},
        {"not extension": "pdf"},
    ]
}

print(Move(Path(".")))

rule = RuleSchema.parse_obj(config)
print("Rule:", rule)

for act in rule.actions:
    print("Action:", act)
    try:
        print("Model:", act.to_model())
    except Exception as e:
        print("Exception:", e)


print("JSON Schema:", RuleSchema.schema_json())
