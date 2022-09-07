import logging
from typing import Any, Dict
from typing import Optional
from typing import Union

from pydantic import BaseModel, root_validator

from organize import console

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class Action(BaseModel):
    class ParseConfig:
        accepts_positional_arg: Union[str, None] = None

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    # def __init__(self, *args, **kwargs) -> None:
    #     # handle positional arguments when calling the class directly
    #     if self.ParseConfig.accepts_positional_arg and len(args) == 1:
    #         kwargs[self.ParseConfig.accepts_positional_arg] = args[0]
    #         super().__init__(**kwargs)
    #         return
    #     super().__init__(*args, **kwargs)

    @root_validator(pre=True)
    def handle_single_str(cls, value):
        # handle positional arguments when parsing a config file.
        if "__positional_arg__" in value and cls is not Action:
            param = cls.ParseConfig.accepts_positional_arg
            if not param:
                raise ValueError(
                    "%s does not accept positional arguments" % cls.__name__
                )
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
            console.pipeline_message(source=self.name, msg=line)

    def print_error(self, msg: str):
        for line in msg.splitlines():
            console.pipeline_error(source=self.name, msg=line)
