"""
Personal file management
"""
from pathlib import Path
import logging
from organize import Rule
from organize import Move
from organize import PaperVDI

logging.basicConfig(level=logging.DEBUG)


def actions(folders, rules: [Rule]):
    for folder in folders:
        for path in Path(folder).expanduser().glob('*.*'):
            for rule in rules:
                if rule.filter.matches(path):
                    yield (rule, path)
                    break


def main(folders, simulate, rules: [Rule]):
    for rule, path in actions(folders=folders, rules=rules):
        file_attributes = rule.filter.parse(path)
        rule.action.run(
            path=path,
            file_attributes=file_attributes,
            simulate=simulate)


if __name__ == '__main__':
    main(
        simulate=True,
        folders=[
            '~/Desktop/__Inbox__',
            '~/Documents/VDI Nachrichten',
        ],
        rules=[
            Rule(filter=PaperVDI(),
                 action=Move('~/Documents/VDI Nachrichten/VDI {year}-{month:02}-{day:02}.pdf'))
        ])
