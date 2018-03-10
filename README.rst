.. image:: https://github.com/tfeldmann/organize/raw/master/docs/images/organize.svg?sanitize=true

.. image:: https://readthedocs.org/projects/organize/badge/?version=latest
  :target: https://organize.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://travis-ci.org/tfeldmann/organize.svg?branch=master
    :target: https://travis-ci.org/tfeldmann/organize

organize
========
**The file management automation tool.**

Install via pip (requirement: Python 3.3+):

``$ pip install organize-tool``


Why you might find this useful
------------------------------
Your desktop is a mess? You cannot find anything in your downloads and
documents? Sorting and renaming all these files by hand is too tedious?
Time to automate it once and benefit from it forever.

*organize* is a command line, open-source alternative to apps like Hazel (macOS)
or File Juggler (Windows).

In your shell, run ``$ organize config`` to edit the configuration and enter
(alternatively create a file ``config.yaml`` at the path shown with
``$ organize config --path``):

- ``config.yaml``:

  .. code-block:: yaml

      rules:
        # move screenshots into "Screenshots" folder
        - folders:
            - ~/Desktop
          filters:
            - Filename:
                startswith: Screen Shot
          actions:
            - Move: ~/Desktop/Screenshots/

        # move incomplete downloads older > 30 days into the trash
        - folders:
            - ~/Downloads
          filters:
            - Extension:
                - download
                - crdownload
                - part
            - LastModified:
                days: 30
                mode: older
          actions:
            - Trash

``$ organize run`` will now move all your screenshots from your desktop into a
subfolder Screenshots (the folder will be created if it does not exist) and put
all incomplete downloader older than 30 days into the trash.
It is that easy.

Feeling insecure? Run ``$ organize sim`` to see what would happen without
touching your files.

But there is more. You want to rename / copy files, run custom shell / python
scripts, match filenames with regular expressions or use placeholder variables?
`organize` has you covered.

Have a look at the full documentation at https://organize.readthedocs.io/.


Functionality
-------------

**Select files by** (filters):

- Extension
- Regular expression
- Last modified date (newer, older)
- Filename (startswith, endswith, contains)

**Organize your files** (actions):

- Move files
- Copy files
- Rename files in place
- Run shell command
- Run inline Python code
- Move into Trash
- Print something to the console

The data from file selection is available in the actions via placeholder
variables.

If you miss a feature please file an issue. Pull requests welcome!


Advanced usage example
----------------------
This is not neccessarily how you *should* organize your files but is a example
of what is possible with placeholder variables:

.. code-block:: yaml

    rules:
      - folders: '~/Documents'
        filters:
          - Extension:
              - pdf
              - docx
          - LastModified
        actions:
          - Move: '~/Documents/{extension.upper}/{lastmodified.year}/'

Given we have two files in our ``~/Documents`` folder named ``script.docx`` from
year 2018 and ``demo.pdf`` from year 2016 this will happen:

- ``script.docx`` will be moved to ``~/Documents/DOCX/2018/script.docx``
- ``demo.pdf`` will be moved to ``~/Documents/PDF/2016/demo.pdf``


Command line interface
----------------------
::

  The file management automation tool.

  Usage:
      organize sim
      organize run
      organize config [--open-folder | --path | --debug]
      organize list
      organize --help
      organize --version

  Arguments:
      sim             Simulate a run. Does not touch your files.
      run             Organizes your files according to your rules.
      config          Open the configuration file in $EDITOR.
      list            List available filters and actions.
      --version       Show program version and exit.
      -h, --help      Show this screen and exit.

  Options:
      -o, --open-folder  Open the folder containing the configuration files.
      -p, --path         Show the path to the configuration file.
      -d, --debug        Print and check your current configuration.

  Full documentation: https://organize.readthedocs.io
