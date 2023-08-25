from textwrap import indent
from typing import Any, Dict, NamedTuple, Union

from schema import Optional, Or, Schema

from organize.console import pipeline_error, pipeline_message


class FilterResult(NamedTuple):
    matches: bool
    updates: dict


class Filter:
    name = None  # type: Union[str, None]
    arg_schema = None  # type: Union[Schema, None]
    schema_support_instance_without_args = False

    @classmethod
    def get_name(cls):
        if cls.name:
            return cls.name
        return cls.__name__.lower()

    @classmethod
    def get_name_schema(cls):
        return Schema(
            Or("not " + cls.get_name(), cls.get_name()),
            name=cls.get_name(),
            description=cls.get_description(),
        )

    @classmethod
    def get_schema(cls):
        name = cls.get_name_schema()

        if cls.arg_schema:
            arg_schema = cls.arg_schema
        else:
            arg_schema = Or(
                str,
                [str],
                Schema({}, ignore_extra_keys=True),
            )

        if cls.schema_support_instance_without_args:
            return Or(name, {name: arg_schema})
        return {
            name: arg_schema,
        }

    @classmethod
    def get_description(cls):
        """the first line of the class docstring"""
        return cls.__doc__.splitlines()[0]

    def run(self, **kwargs: Dict) -> FilterResult:
        return self.pipeline(dict(kwargs))

    def pipeline(self, args: dict) -> FilterResult:
        raise NotImplementedError

    def print(self, *msg: str) -> None:
        """print a message for the user"""
        text = " ".join(str(x) for x in msg)
        for line in text.splitlines():
            pipeline_message(self.get_name(), line)

    def print_error(self, msg: str):
        for line in msg.splitlines():
            pipeline_error(self.get_name(), line)

    def set_logic(self, inverted=False):
        self.inverted = inverted

    def __str__(self) -> str:
        """Return filter name and properties"""
        return self.get_name()

    def __repr__(self) -> str:
        return f"<{str(self)}>"

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
