from enum import Enum
from typing import Union

from pydantic import BaseModel, root_validator
from typing_extensions import Literal


class Action(BaseModel):
    class Settings:
        accepts_positional_arg: Union[str, None] = None

    def __init__(self, *args, **kwargs) -> None:
        if self.Settings.accepts_positional_arg and len(args) == 1:
            kwargs[self.Settings.accepts_positional_arg] = args[0]
            super().__init__(**kwargs)
            return
        super().__init__(*args, **kwargs)

    @root_validator(pre=True)
    def handle_single_str(cls, value):
        if "__positional_arg__" in value:
            param = cls.Settings.accepts_positional_arg
            if not param:
                raise ValueError("Non-dict arguments are not accepted")
            param_val = value.pop("__positional_arg__")
            return {param: param_val, **value}
        return value


class ConflictOptions(str, Enum):
    rename_new = "rename_new"
    overwrite = "overwrite"


class Move(Action):
    name: Literal["move"] = "move"

    dest: str
    on_conflict: ConflictOptions = ConflictOptions.rename_new
    rename_template: str = "{name} {counter}{extension}"
    filesystem: Union[None, str] = None

    class Settings:
        accepts_positional_arg = "dest"


class Copy(Action):
    name: Literal["copy"] = "copy"

    dest: str
    on_conflict: ConflictOptions = ConflictOptions.rename_new
    rename_template: str = "{name} {counter}{extension}"
    filesystem: Union[None, str] = None


## -- end actions
