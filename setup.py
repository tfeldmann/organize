import os
import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 0):
    raise EnvironmentError('organize requires Python 3.3+')

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in
# file!
with open(os.path.join(here, 'README.rst')) as f:
    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, 'organize', '__version__.py')) as f:
    exec(f.read(), about)

install_requires = [
    'appdirs',
    'docopt',
    'pyyaml',
    'Send2Trash',
    'clint',
    'colorama',
]
if sys.version_info < (3, 5):
    install_requires.append('typing')
    install_requires.append('pathlib2')

setup(
    name='organize-tool',
    version=about['__version__'],
    description='The file management automation tool.',
    long_description=long_description,
    author='Thomas Feldmann',
    author_email='mail@tfeldmann.de',
    url='https://github.com/tfeldmann/organize',
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': ['organize=organize.cli:main'],
    },
    install_requires=install_requires,
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
)
