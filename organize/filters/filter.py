from typing import Dict, NamedTuple, Union

from pydantic import BaseModel, root_validator

from organize import console


class FilterResult(NamedTuple):
    matches: bool
    updates: dict


class Filter(BaseModel):
    filter_is_inverted: bool = False

    class ParseConfig:
        accepts_positional_arg: Union[str, None] = None

    class Config:
        extra = "forbid"
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    @root_validator(pre=True)
    def handle_single_str(cls, value):
        # handle positional arguments when parsing a config file.
        if "__positional_arg__" in value:
            param = cls.ParseConfig.accepts_positional_arg
            if not param:
                raise ValueError("Non-dict arguments are not accepted")
            param_val = value.pop("__positional_arg__")
            return {param: param_val, **value}
        return value

    def __init__(self, *args, **kwargs) -> None:
        # handle positional arguments when calling the class directly
        if self.ParseConfig.accepts_positional_arg and len(args) == 1:
            kwargs[self.ParseConfig.accepts_positional_arg] = args[0]
            super().__init__(**kwargs)
            return
        super().__init__(*args, **kwargs)

    def run(self, **kwargs: Dict) -> FilterResult:
        return self.pipeline(dict(kwargs))

    def pipeline(self, args: dict) -> FilterResult:
        raise NotImplementedError

    def print(self, *msg: str) -> None:
        """print a message for the user"""
        text = " ".join(str(x) for x in msg)
        for line in text.splitlines():
            console.pipeline_message(self.name, line)

    def print_error(self, msg: str):
        for line in msg.splitlines():
            console.pipeline_error(self.name, line)
