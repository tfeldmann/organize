from organize import Config
from organize.cli import EXAMPLE_CONFIG
from organize.output import JSONL, Default


def test_example_config(msg_output):
    config = Config.from_string(EXAMPLE_CONFIG)
    config.execute(simulate=False, output=msg_output)
    assert msg_output.messages == ["Hello, World!"]
    config.execute(simulate=False, output=Default())
    config.execute(simulate=False, output=JSONL())
