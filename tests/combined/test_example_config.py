from organize import Config
from organize.find_config import EXAMPLE_CONFIG
from organize.output import JSONL, Default


def test_example_config(testoutput):
    config = Config.from_string(EXAMPLE_CONFIG)
    config.execute(simulate=False, output=testoutput)
    assert testoutput.messages == ["Hello, World!"]
    config.execute(simulate=False, output=Default())
    config.execute(simulate=False, output=JSONL())
