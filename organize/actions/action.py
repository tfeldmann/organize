from schema import Or, Schema, Optional
from typing import Any, Dict, Optional as tyOptional, Callable


class Error(Exception):
    pass


class TemplateAttributeError(Error):
    pass


class Action:
    print_hook = None  # type: Optional[Callable]
    print_error_hook = None  # type: Optional[Callable]

    name = None
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

    def run(self, **kwargs) -> tyOptional[Dict[str, Any]]:
        return self.pipeline(kwargs)

    def pipeline(self, args: dict) -> tyOptional[Dict[str, Any]]:
        raise NotImplementedError

    def print(self, msg, *args, **kwargs) -> None:
        """print a message for the user"""
        if callable(self.print_hook):
            self.print_hook(name=self.name, msg=msg, *args, **kwargs)

    def print_error(self, msg: str):
        if callable(self.print_error_hook):
            self.print_error_hook(name=self.name, msg=msg)

    @staticmethod
    def fill_template_tags(msg: str, args) -> str:
        try:
            return msg.format(**args)
        except AttributeError as exc:
            cause = exc.args[0]
            raise TemplateAttributeError(
                'Missing template variable %s for "%s"' % (cause, msg)
            )

    def __str__(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return "<%s>" % str(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__
