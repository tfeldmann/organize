from typing import List
from collections import namedtuple
import yaml
from organize import actions, filters

Rule = namedtuple('Rule', 'filters actions folders')


class Config:

    def __init__(self, config: str):
        self.config = yaml.load(config)

    @property
    def rules(self) -> List[Rule]:
        """ A list of instantiated Rules
        """
        def first_key(d):
            return list(d.keys())[0]

        result = []
        for rule_item in self.config['rules']:
            # parse filters
            rule_filters = []
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
                rule_filters.append(f)

            # parse actions
            rule_actions = []
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
                rule_actions.append(a)

            rule = Rule(
                filters=rule_filters,
                actions=rule_actions,
                folders=rule_item['folders'])
            result.append(rule)
        return result

    class Error(Exception):
        pass
