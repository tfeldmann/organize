from typing import Union

from organize.action import HasActionConfig
from organize.filter import HasFilterConfig

SenderType = Union[HasActionConfig, HasFilterConfig, str]


def sender_name(sender: SenderType) -> str:
    if isinstance(sender, HasFilterConfig):
        return sender.filter_config.name
    elif isinstance(sender, HasActionConfig):
        return sender.action_config.name
    return str(sender)
