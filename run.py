from organize import Config, Rule
from organize.actions import Echo
from organize.filters import Name

echo = Echo("{name.upper()} {% if name.upper() == 'RUN' %}{1 / 0}{% endif %}")

config = Config(
    rules=[
        Rule(
            name="Say something",
            locations=[".", "/asd", "~/Desktop"],
            filters=[Name()],
            actions=[echo],
        ),
    ]
)
config.execute(simulate=False)
