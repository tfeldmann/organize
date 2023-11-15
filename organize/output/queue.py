from .jsonl import JSONL, EventType


class QueueOutput(JSONL):
    def __init__(self):
        self.queue = []

    def start(self, *args, **kwargs):
        self.queue.clear()
        super().start(*args, **kwargs)

    def emit_event(self, event: EventType):
        self.queue.append(event)

    @property
    def messages(self):
        return [x for x in self.queue if x.type == "MSG"]
