"""
Personal file management tool.

Usage:
    organize
    organize run
    organize undo
    organize list
    organize config
    organize --help
    organize --version

Arguments:
    run             Applies the actions. No simulation
    undo            Undo the last organization run
    list            List available actions and filters
    config          Open configuration in %{EDITOR}

Options:
    --version       Show program version and exit.
    -h, --help      Show this screen and exit.
"""

import logging
from pathlib import Path

from organize import Rule
from organize import filters
from organize import actions

from docopt import docopt

__version__ = '0.0'
logging.basicConfig(level=logging.DEBUG)


def iter_actions(folders, rules: [Rule]):
    for folder in folders:
        for path in Path(folder).expanduser().glob('*.*'):
            for rule in rules:
                if rule.filter.matches(path):
                    yield (rule, path)
                    break


def main(folders, simulate, rules: [Rule]):
    for rule, path in iter_actions(folders=folders, rules=rules):
        file_attributes = rule.filter.parse(path)
        rule.action.run(
            path=path,
            file_attributes=file_attributes,
            simulate=simulate)


if __name__ == '__main__':
    args = docopt(__doc__, version=__version__, help=True)
    if args['list']:
        print('Available filters:')
        print('Available actions:')
    elif args['config']:
        print('Opening your config file')

    simulate = not args['run']
    main(
        simulate=simulate,
        folders=[
            '~/Desktop/__Inbox__',
            '~/Documents/VDI Nachrichten',
        ],
        rules=[
            Rule(filter=filters.PaperVDI(),
                 action=actions.Move('~/Documents/VDI Nachrichten/VDI {year}-{month:02}-{day:02}.pdf'))
        ])
