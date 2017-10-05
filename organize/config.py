import logging
from typing import List
from collections import namedtuple
import yaml
from organize import actions, filters

logger = logging.getLogger(__name__)
Rule = namedtuple('Rule', 'filters actions folders')


def first_key(d):
    return list(d.keys())[0]


def flatten(arr):
    if arr == []:
        return []
    elif not isinstance(arr, list):
        return [arr]
    else:
        return flatten(arr[0]) + flatten(arr[1:])


class Config:

    def __init__(self, config: str):
        self.config = yaml.load(config)

    def parse_folders(self, rule_item):
        yield from flatten(rule_item['folders'])

    def parse_filters(self, rule_item):
        for filter_item in rule_item['filters']:
            if isinstance(filter_item, dict):
                name = first_key(filter_item)
                args = filter_item[name]
                f = getattr(filters, name)(**args)
            elif isinstance(filter_item, str):
                name = filter_item
                f = getattr(filters, name)()
            else:
                raise self.Error('Unknown filter type: %s' % filter_item)
            yield f

    def parse_actions(self, rule_item):
        for action_item in rule_item['actions']:
            if isinstance(action_item, dict):
                name = first_key(action_item)
                args = action_item[name]
                a = getattr(actions, name)(**args)
            elif isinstance(action_item, str):
                name = action_item
                a = getattr(actions, name)()
            else:
                raise self.Error('Unknown action type: %s' % action_item)
            yield a

    @property
    def rules(self) -> List[Rule]:
        """:returns: A list of instantiated Rules
        """
        result = []
        for i, rule_item in enumerate(self.config['rules']):
            rule_folders = list(self.parse_folders(rule_item))
            rule_filters = list(self.parse_filters(rule_item))
            rule_actions = list(self.parse_actions(rule_item))

            if not rule_folders:
                logger.warning('No folders given for rule %s!', i + 1)
            if not rule_filters:
                logger.warning('No filters given for rule %s!', i + 1)
            if not rule_actions:
                logger.warning('No actions given for rule %s!', i + 1)

            rule = Rule(
                folders=rule_folders,
                filters=rule_filters,
                actions=rule_actions)
            result.append(rule)
        return result

    class Error(Exception):
        pass
