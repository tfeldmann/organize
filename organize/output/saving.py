from typing import List

from .jsonl import JSONL, EventType


class SavingOutput(JSONL):
    """
    Saves all the incoming event messages of the latest run.
    """

    def __init__(self) -> None:
        self.queue: List[EventType] = []

    def start(self, *args, **kwargs) -> None:
        self.queue.clear()
        super().start(*args, **kwargs)

    def emit_event(self, event: EventType) -> None:
        self.queue.append(event)

    def _messages_of_kind(self, kind: str) -> List:
        return [x for x in self.queue if x.type == kind]

    @property
    def msg_start(self):
        result = self._messages_of_kind("START")
        if len(result) != 1:
            raise ValueError("Multiple start events found")
        return result[0]

    @property
    def msg_msg(self):
        return self._messages_of_kind("MSG")

    @property
    def msg_report(self):
        result = self._messages_of_kind("REPORT")
        if len(result) != 1:
            raise ValueError("Multiple reports found")
        return result[0]

    @property
    def messages(self):
        return [x.msg for x in self.queue if x.type == "MSG"]
