from typing_extensions import Protocol, runtime_checkable

from .resource import Resource


@runtime_checkable
class Filter(Protocol):
    def pipeline(self, res: dict) -> bool:
        ...


class Not:
    def __init__(self, filter: Filter):
        self.filter = filter

    def pipeline(self, res: dict) -> dict:
        return not self.filter.pipeline(res)

    def __repr__(self):
        return f"Not({self.filter})"


class Or:
    def __init__(self, *filters):
        self.filters = filters

    def pipeline(self, res: Resource) -> bool:
        # we cannot exit early if a filter doesn't match because we may need the
        # generated vars of this filter
        results = [f.pipeline(res) for f in self.filters]
        return any(results)

    def __repr__(self):
        filters = ", ".join(str(x) for x in self.filters)
        return f"Or({filters})"


class Any:
    pass


class All:
    pass
