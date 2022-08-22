from enum import Enum
from typing import Union, List

from pydantic import BaseModel, root_validator
from typing_extensions import Literal
from typing import NamedTuple
from organize.console import pipeline_error, pipeline_message

## for extension filter
# def convert_to_list(cls, v):
#     if not v:
#         return []
#     if isinstance(v, str):
#         return v.split()
#     return v


# def normalize_to_list(field_name: str):
#     return validator(field_name, allow_reuse=True, pre=True)(convert_to_list)
from textwrap import indent
from typing import Any, Dict, NamedTuple, Union

from schema import Optional, Or, Schema

from organize.console import pipeline_error, pipeline_message


class FilterResult(NamedTuple):
    matches: bool
    updates: dict


class Filter(BaseModel):
    filter_is_inverted: bool = False

    # def __init__(self, *args, **kwargs) -> None:
    #     # handle positional arguments when calling the class directly
    #     if self.Settings.accepts_positional_arg and len(args) == 1:
    #         kwargs[self.Settings.accepts_positional_arg] = args[0]
    #         super().__init__(**kwargs)
    #         return
    #     super().__init__(*args, **kwargs)

    def run(self, **kwargs: Dict) -> FilterResult:
        return self.pipeline(dict(kwargs))

    def pipeline(self, args: dict) -> FilterResult:
        raise NotImplementedError

    def print(self, *msg: str) -> None:
        """print a message for the user"""
        text = " ".join(str(x) for x in msg)
        for line in text.splitlines():
            pipeline_message(self.name, line)

    def print_error(self, msg: str):
        for line in msg.splitlines():
            pipeline_error(self.name, line)

    class Config:
        arbitrary_types_allowed = True
        extra = "forbid"
        underscore_attrs_are_private = True
        accepts_positional_arg: Union[str, None] = None

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


class Name(Filter):
    name: Literal["name"] = "name"

    match: str
    startswith: Union[str, List[str]] = ""
    contains: Union[str, List[str]] = ""
    endswith: Union[str, List[str]] = ""
    case_sensitive: bool = True

    class Config:
        accepts_positional_arg = "match"


class Empty(Filter):
    name: Literal["empty"] = "empty"

    def pipeline(self, args: dict) -> FilterResult:
        fs = args["fs"]  # type: FS
        fs_path = args["fs_path"]  # type: str

        if fs.isdir(fs_path):
            result = fs.isempty(fs_path)
        else:
            result = fs.getsize(fs_path) == 0

        return FilterResult(matches=result, updates={})

    class Config:
        accepts_positional_arg = "match"
