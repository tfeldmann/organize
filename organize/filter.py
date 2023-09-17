from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class Filter(Protocol):
    def pipeline(self, res: dict) -> dict:
        pass


class Not:
    def __init__(self, filter: Filter):
        self.filter = filter

    def pipeline(self, res: dict) -> dict:
        return not self.filter.pipeline(res)

    def __repr__(self):
        return f"Not({self.filter})"


class Or:
    pass


class Any:
    pass


class All:
    pass
