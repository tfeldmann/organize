import logging
from typing import ClassVar, NamedTuple, Protocol, runtime_checkable

from .output import Output
from .resource import Resource


class FilterConfig(NamedTuple):
    name: str
    files: bool
    dirs: bool


@runtime_checkable
class Filter(Protocol):
    filter_config: ClassVar[FilterConfig]

    def pipeline(self, res: Resource, output: Output) -> bool:
        ...


class Not:
    def __init__(self, filter: Filter):
        self.filter = filter

    def pipeline(self, res: Resource, output: Output) -> bool:
        return not self.filter.pipeline(res=res, output=output)

    def __repr__(self):
        return f"Not({self.filter})"

    @property
    def filter_config(self):
        return self.filter.filter_config


class All:
    def __init__(self, *filters: Filter):
        self.filters = filters

    def pipeline(self, res: Resource, output: Output) -> bool:
        for filter in self.filters:
            try:
                match = filter.pipeline(res, output=output)
                if not match:
                    return False
            except Exception as e:
                output.msg(res=res, level="error", msg=str(e))
                logging.exception(e)
                return False
        return True


class Any:
    def __init__(self, *filters: Filter):
        self.filters = filters

    def pipeline(self, res: Resource, output: Output) -> bool:
        for filter in self.filters:
            result = False
            try:
                match = filter.pipeline(res, output=output)
                if match:
                    result = True
            except Exception as e:
                output.msg(res=res, level="error", msg=str(e))
                logging.exception()
        return result
