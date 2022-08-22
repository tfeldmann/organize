from fs.base import FS
from enum import Enum
from typing import Optional, Union, Dict, Any

from pydantic import BaseModel, root_validator
from typing_extensions import Literal
from .console import pipeline_error, pipeline_message


class Action(BaseModel):
    class Config:
        # pydantic
        arbitrary_types_allowed = True
        extra = "forbid"
        underscore_attrs_are_private = True
        # organize
        accepts_positional_arg: Union[str, None] = None

    # def __init__(self, *args, **kwargs) -> None:
    #     # handle positional arguments when calling the class directly
    #     if self.Settings.accepts_positional_arg and len(args) == 1:
    #         kwargs[self.Settings.accepts_positional_arg] = args[0]
    #         super().__init__(**kwargs)
    #         return
    #     super().__init__(*args, **kwargs)

    @root_validator(pre=True)
    def handle_single_str(cls, value):
        # handle positional arguments when parsing a config file.
        if "__positional_arg__" in value:
            param = cls.Config.accepts_positional_arg
            if not param:
                raise ValueError("Non-dict arguments are not accepted")
            param_val = value.pop("__positional_arg__")
            return {param: param_val, **value}
        return value

    def run(self, simulate: bool, **kwargs) -> Optional[Dict[str, Any]]:
        return self.pipeline(kwargs, simulate=simulate)

    def pipeline(self, args: dict, simulate: bool) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def print(self, *msg) -> None:
        """print a message for the user"""
        text = " ".join(str(x) for x in msg)
        for line in text.splitlines():
            pipeline_message(source=self.get_name(), msg=line)

    def print_error(self, msg: str):
        for line in msg.splitlines():
            pipeline_error(source=self.get_name(), msg=line)


class ConflictOptions(str, Enum):
    rename_new = "rename_new"
    overwrite = "overwrite"


class Move(Action):
    name: Literal["move"] = "move"

    dest: str
    on_conflict: ConflictOptions = ConflictOptions.rename_new
    rename_template: str = "{name} {counter}{extension}"
    filesystem: Union[FS, str, None] = None

    class Config:
        accepts_positional_arg = "dest"


class Copy(Action):
    name: Literal["copy"] = "copy"

    dest: str
    on_conflict: ConflictOptions = ConflictOptions.rename_new
    rename_template: str = "{name} {counter}{extension}"
    filesystem: Union[None, str] = None


## -- end actions
