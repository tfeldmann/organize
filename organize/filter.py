import logging
from typing import ClassVar, Iterable, NamedTuple, Protocol, runtime_checkable

from .output import Output
from .resource import Resource


class FilterConfig(NamedTuple):
    name: str
    files: bool
    dirs: bool


class HasFilterPipeline(Protocol):
    def pipeline(self, res: Resource, output: Output) -> bool:
        ...


class HasFilterConfig(Protocol):
    filter_config: FilterConfig


@runtime_checkable
class Filter(HasFilterPipeline, HasFilterConfig, Protocol):
    def __init__(self, *args, **kwargs) -> None:
        # allow any amount of args / kwargs for BaseModel and dataclasses.
        ...


class Not:
    def __init__(self, filter: Filter):
        self.filter = filter
        self.filter_config = self.filter.filter_config

    def pipeline(self, res: Resource, output: Output) -> bool:
        return not self.filter.pipeline(res=res, output=output)

    def __repr__(self):
        return f"Not({self.filter})"


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
        assert res.path is not None, "Filters don't support standalone mode."
        for filter in self.filters:
            result = False
            try:
                match = filter.pipeline(res, output=output)
                if match:
                    result = True
            except Exception as e:
                output.msg(res=res, level="error", msg=str(e))
                logging.exception(e)
        return result
