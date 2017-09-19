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
__version__ = '0.0'

import logging
from pathlib import Path

import appdirs
from docopt import docopt

from config import CONFIG
from organize import Rule


app_dirs = appdirs.AppDirs('organize')
config_dir = Path(app_dirs.user_config_dir)
log_dir = Path(app_dirs.user_log_dir)
for p in (config_dir, log_dir):
    p.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def iter_actions(folders: [str], rules: [Rule]):
    for folder in folders:
        logger.info('Folder: %s', folder)
        for path in Path(folder).expanduser().glob('*.*'):
            for rule in rules:
                if rule.filter.matches(path):
                    yield (rule, path)
                    break


def main(folders: [str], rules: [Rule], simulate: bool):
    for rule, path in iter_actions(folders=folders, rules=rules):
        file_attributes = rule.filter.parse(path)
        rule.action.run(
            path=path.resolve(),
            file_attributes=file_attributes,
            simulate=simulate)


if __name__ == '__main__':
    args = docopt(__doc__, version=__version__, help=True)

    if args['config']:
        print(app_dirs.user_config_dir)
        print('Opening your config folder...')
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
        for config in CONFIG:
            main(folders=config['folders'],
                 rules=config['rules'],
                 simulate=args['simulate'])
