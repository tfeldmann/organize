import logging
from typing import Any, Dict
from typing import Optional as tyOptional
from typing import Union

from schema import Optional, Or, Schema

from organize.console import pipeline_error, pipeline_message

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class Action:
    name = None  # type: Union[str, None]
    arg_schema = None
    schema_support_instance_without_args = False

    @classmethod
    def get_name(cls):
        if cls.name:
            return cls.name
        return cls.__name__.lower()

    @classmethod
    def get_schema(cls):
        if cls.arg_schema:
            arg_schema = cls.arg_schema
        else:
            arg_schema = Or(
                str,
                [str],
                Schema({}, ignore_extra_keys=True),
            )
        if cls.schema_support_instance_without_args:
            return Or(
                cls.get_name(),
                {
                    cls.get_name(): arg_schema,
                },
            )
        return {
            cls.get_name(): arg_schema,
        }

    def run(self, simulate: bool, **kwargs) -> tyOptional[Dict[str, Any]]:
        return self.pipeline(kwargs, simulate=simulate)

    def pipeline(self, args: dict, simulate: bool) -> tyOptional[Dict[str, Any]]:
        raise NotImplementedError

    def print(self, *msg) -> None:
        """print a message for the user"""
        text = " ".join(str(x) for x in msg)
        for line in text.splitlines():
            pipeline_message(source=self.get_name(), msg=line)

    def print_error(self, msg: str):
        for line in msg.splitlines():
            pipeline_error(source=self.get_name(), msg=line)

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return "<%s>" % str(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
