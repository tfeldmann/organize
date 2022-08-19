from enum import Enum
from typing import Union, List

from pydantic import BaseModel, root_validator
from typing_extensions import Literal
from typing import NamedTuple


## for extension filter
# def convert_to_list(cls, v):
#     if not v:
#         return []
#     if isinstance(v, str):
#         return v.split()
#     return v


# def normalize_to_list(field_name: str):
#     return validator(field_name, allow_reuse=True, pre=True)(convert_to_list)


class FilterResult(NamedTuple):
    matches: bool
    updates: dict


class Filter(BaseModel):
    filter_is_inverted: bool = False

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

    class Settings:
        accepts_positional_arg = "match"


class Empty(Filter):
    name: Literal["empty"] = "empty"

    class Settings:
        accepts_positional_arg = "match"
