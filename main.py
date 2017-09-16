"""
The personal file management tool.

Usage:
    organize simulate
    organize run
    organize undo
    organize list
    organize config
    organize --help
    organize --version

Arguments:
    simulate        Simulate organizing your files. This allows you to check your rules.
    run             Applies the actions. No simulation.
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

import appdirs
from docopt import docopt

__version__ = '0.0'
logging.basicConfig(level=logging.INFO)

import config
print(config.CONFIG)

# config folder
app_dirs = appdirs.AppDirs('organize')
config_dir = Path(app_dirs.user_config_dir)
config_dir.mkdir(parents=True, exist_ok=True)


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

    if args['config']:
        print('Opening your config folder...')
        print(app_dirs.user_config_dir)
        import webbrowser
        webbrowser.open(config_dir.as_uri())

    elif args['list']:
        print('Available filters:')
        print(' - TODO')
        print('')
        print('Available actions:')
        print(' - TODO')
        print('')

    elif args['undo']:
        print('Do you want to undo the last action? N / y / (s)how')

    else:
        main(simulate=args['simulate'])
