import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'readme.rst' is present in your MANIFEST.in
# file!
with open(os.path.join(here, 'readme.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, 'organize', '__version__.py')) as f:
    exec(f.read(), about)


setup(
    name='organize-tool',
    version=about['__version__'],
    description='The file management automation tool.',
    long_description=long_description,
    author='Thomas Feldmann',
    author_email='mail@tfeldmann.de',
    url='https://github.com/tfeldmann/organize',
    packages=find_packages(exclude=['test']),
    entry_points={
        'console_scripts': ['organize=organize.cli:cli'],
    },
    install_requires=['appdirs', 'docopt', 'slate3k', 'pyyaml', 'Send2Trash'],
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
)
