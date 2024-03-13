from __future__ import annotations

import logging
from typing import TYPE_CHECKING, NamedTuple, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .output import Output
    from .resource import Resource


class FilterConfig(NamedTuple):
    name: str
    files: bool
    dirs: bool


@runtime_checkable
class HasFilterConfig(Protocol):
    filter_config: FilterConfig


class HasFilterPipeline(Protocol):
    def pipeline(self, res: Resource, output: Output) -> bool: ...  # pragma: no cover


@runtime_checkable
class Filter(HasFilterPipeline, HasFilterConfig, Protocol):
    def __init__(self, *args, **kwargs) -> None:
        # allow any amount of args / kwargs for BaseModel and dataclasses.
        ...  # pragma: no cover


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
                output.msg(res=res, level="error", msg=str(e), sender=filter)
                logging.exception(e)
                return False
        return True


class Any:
    def __init__(self, *filters: Filter):
        self.filters = filters

    def pipeline(self, res: Resource, output: Output) -> bool:
        result = False
        for filter in self.filters:
            try:
                match = filter.pipeline(res, output=output)
                if match:
                    result = True
            except Exception as e:
                output.msg(res=res, level="error", msg=str(e), sender=filter)
                logging.exception(e)
        return result
