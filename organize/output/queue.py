from .raw import Event, RawOutput


class QueueOutput(RawOutput):
    def __init__(self):
        self.queue = []

    def start(self, *args, **kwargs):
        self.queue.clear()
        super().start(*args, **kwargs)

    def _output(self, item: Event):
        self.queue.append(item)

    @property
    def messages(self):
        return [x for x in self.queue if x.type == "MSG"]
