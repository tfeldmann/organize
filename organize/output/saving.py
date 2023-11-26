from typing import List

from .jsonl import JSONL, EventType


class SavingOutput(JSONL):
    """
    Saves all the incoming event messages of the latest run.
    """

    def __init__(self):
        self.queue: List[EventType] = []

    def start(self, *args, **kwargs):
        self.queue.clear()
        super().start(*args, **kwargs)

    def emit_event(self, event: EventType):
        self.queue.append(event)

    def _messages_of_kind(self, kind: str):
        return [x for x in self.queue if x.type == kind]

    @property
    def msg_start(self):
        return self._messages_of_kind("START")

    @property
    def msg_msg(self):
        return self._messages_of_kind("MSG")

    @property
    def msg_report(self):
        return self._messages_of_kind("REPORT")

    @property
    def messages(self):
        return [x.msg for x in self.queue if x.type == "MSG"]
