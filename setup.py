import os
import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 3):
    raise EnvironmentError('Python 3.3+ required')

ROOT = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in
# file!
with open(os.path.join(ROOT, 'README.rst')) as f:
    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(ROOT, 'organize', '__version__.py')) as f:
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
if sys.version_info < (3, 6):
    install_requires.append('pathlib2')

tests_require = ['pytest', 'mock']

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=long_description,
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=find_packages(exclude=['tests', 'docs']),
    entry_points={
        'console_scripts': ['organize=organize.main:main'],
    },
    python_requires='>=3.3',
    install_requires=install_requires,
    tests_require=tests_require,
    license=about['__license__'],
    keywords='file management automation tool organization rules yaml',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Natural Language :: English',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    project_urls={
        'Documentation': 'http://organize.readthedocs.io',
    },
)
