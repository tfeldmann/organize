from schema import Schema, Optional, Or  # type: ignore
from textwrap import indent
from typing import Any, Dict, Union, NamedTuple


class FilterResult(NamedTuple):
    matches: bool
    updates: dict


class Filter:
    print_hook = None
    print_error_hook = None

    name: str
    arg_schema: Schema
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
        if callable(self.print_hook):
            self.print_hook(name=self.name, msg=msg)

    def print_error(self, msg: str):
        if callable(self.print_error_hook):
            self.print_error_hook(name=self.name, msg=msg)

    def __str__(self) -> str:
        """Return filter name and properties"""
        return self.get_name()

    def __repr__(self) -> str:
        return "<%s>" % str(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
