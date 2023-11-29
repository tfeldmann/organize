import pytest
from conftest import make_files

from organize import Config, Rule
from organize.actions import Echo
from organize.filters import Name


@pytest.mark.skip
def test_api(fs, testoutput):
    make_files(["foo.txt", "bar.txt", "baz.txt"], "test")

    echo = Echo("{name.upper()}{% if name.upper() == 'RUN' %}{1 / 0}{% endif %}")

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
    assert testoutput.messages == ["FOO", "BAR", "BAZ"]
