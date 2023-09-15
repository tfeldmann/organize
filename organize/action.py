from typing_extensions import runtime_checkable, Protocol


@runtime_checkable
class Action(Protocol):
    def pipeline(res: dict) -> dict:
        pass
