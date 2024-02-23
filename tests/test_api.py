from conftest import make_files

from organize import Config, Rule
from organize.actions import Echo
from organize.filters import Name


def test_api(fs, testoutput):
    make_files(["foo.txt", "bar.txt", "baz.txt"], "test")

    echo = Echo("{name.upper()}{% if name.upper() == 'FOO' %}FOO{% endif %}")

    config = Config(
        rules=[
            Rule(
                name="Say something",
                locations=["/test"],
                filters=[Name()],
                actions=[echo],
            ),
        ]
    )
    config.execute(simulate=False, output=testoutput)
    assert testoutput.messages == ["BAR", "BAZ", "FOOFOO"]
