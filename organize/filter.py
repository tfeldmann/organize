from typing_extensions import runtime_checkable, Protocol


@runtime_checkable
class Filter(Protocol):
    def match(self, res: dict) -> bool:
        pass

    def pipeline(self, res: dict) -> dict:
        pass


class Not:
    def __init__(self, filter: Filter):
        self.filter = filter

    def match(self, res: dict) -> bool:
        return not self.filter.match(res)

    def pipeline(self, res: dict) -> dict:
        return self.filter.pipeline(res)

    def __repr__(self):
        return f"Not({self.filter})"


class Or:
    pass


class Any:
    pass


class All:
    pass
