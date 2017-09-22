"""
The personal file management tool.

Usage:
    organize sim
    organize run
    organize config
    organize --help
    organize --version

Arguments:
    sim             Simulate organizing your files. This allows you to check your rules.
    run             Applies the actions. No simulation.
    config          Open the organize config folder

Options:
    --version       Show program version and exit.
    -h, --help      Show this screen and exit.
"""
__version__ = '0.0'

import logging
from pathlib import Path

import appdirs
from docopt import docopt

from organize.config import Rule, Config


app_dirs = appdirs.AppDirs('organize')
config_dir = Path(app_dirs.user_config_dir)
log_dir = Path(app_dirs.user_log_dir)
for p in (config_dir, log_dir):
    p.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def execute_rules(rules, simulate: bool):
    # TODO: Return sorted [(path, filters, actions), ...] and check for multiple
    # rules applying to the same path
    def first(a):
        return a[0]

    for rule in rules:
        filter_ = first(rule.filters)
        action_ = first(rule.actions)
        logger.debug('Filter: %s, Action: %s', filter_, action_)

        for folder in rule.folders:
            logger.debug('Folder: %s', folder)
            for path in Path(folder).expanduser().glob('*.*'):
                logger.debug('Path: %s', path)
                if filter_.matches(path):
                    file_attributes = filter_.parse(path)
                    action_.run(
                        path=path.resolve(),
                        file_attributes=file_attributes,
                        simulate=simulate)


if __name__ == '__main__':
    args = docopt(__doc__, version=__version__, help=True)

    if args['config']:
        print(app_dirs.user_config_dir)
        import webbrowser
        webbrowser.open(config_dir.as_uri())

    # elif args['list']:
    #     print('Available filters:')
    #     print(' - TODO')
    #     print('')
    #     print('Available actions:')
    #     print(' - TODO')
    #     print('')

    else:
        with open('config.yaml') as f:
            config = Config(f.read())
        execute_rules(config.rules, simulate=args['sim'])
