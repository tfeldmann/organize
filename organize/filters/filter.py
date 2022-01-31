from schema import Schema, Optional, Or
from textwrap import indent
from typing import Any, Dict, Union, NamedTuple
from organize.console import pipeline_message, pipeline_error


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

    def print(self, msg: str) -> None:
        """print a message for the user"""
        pipeline_message(self.get_name(), msg)

    def print_error(self, msg: str):
        pipeline_error(self.get_name(), msg)

    def __str__(self) -> str:
        """Return filter name and properties"""
        return self.get_name()

    def __repr__(self) -> str:
        return "<%s>" % str(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
