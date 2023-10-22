from .raw import Event, RawOutput


class JSONL(RawOutput):
    def _output(self, item: Event):
        print(item.model_dump_json())
