.. image:: https://github.com/tfeldmann/organize/raw/master/docs/images/organize.svg?sanitize=true

.. image:: https://readthedocs.org/projects/organize/badge/?version=latest
  :target: https://organize.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://travis-ci.org/tfeldmann/organize.svg?branch=master
    :target: https://travis-ci.org/tfeldmann/organize

organize
========
**The file management automation tool.**

Install via pip (requirement: Python 3.4+):

On macOS / Windows:
``$ pip3 install organize-tool``

On Linux:
``$ sudo pip3 install organize-tool``

Full documentation at https://organize.readthedocs.io/.


Why you might find this useful
------------------------------
Your desktop is a mess? You cannot find anything in your downloads and
documents? Sorting and renaming all these files by hand is too tedious?
Time to automate it once and benefit from it forever.

*organize* is a command line, open-source alternative to apps like Hazel (macOS)
or File Juggler (Windows).

In your shell, run ``$ organize config`` to edit the configuration:

- ``config.yaml``:

  .. code-block:: yaml

      rules:
        # move screenshots into "Screenshots" folder
        - folders:
            - ~/Desktop
          filters:
            - filename:
                startswith: 'Screen Shot'
          actions:
            - move: ~/Desktop/Screenshots/

        # move incomplete downloads older > 30 days into the trash
        - folders:
            - ~/Downloads
          filters:
            - extension:
                - download
                - crdownload
                - part
            - lastmodified:
                days: 30
                mode: older
          actions:
            - trash

(alternatively you can run ``$ organize config --path`` to see the full path to
your ``config.yaml``)

``$ organize run`` will now...

- move all your screenshots from your desktop a "Screenshots" subfolder
  (the folder will be created if it does not exist)
- put all incomplete downloads older than 30 days into the trash

It is that easy.

Feeling insecure? Run ``$ organize sim`` to see what would happen without
touching your files.

But there is more. You want to rename / copy files, run custom shell- or python
scripts, match filenames with regular expressions or use placeholder variables?
`organize` has you covered.


Advanced usage example
----------------------
This example shows some advanced features like placeholder variables, pluggable
actions and recursion through subfolders:

.. code-block:: yaml

    rules:
      - folders: ~/Documents/**/*
        filters:
          - extension:
              - pdf
              - docx
          - lastmodified
        actions:
          - move: '~/Documents/{extension.upper}/{lastmodified.year}-{lastmodified.month:02}/'
          - shell: 'open "{path}"'

Given we have two files in our ``~/Documents`` folder (or any of its subfolders)
named ``script.docx`` from january 2018 and ``demo.pdf`` from december 2016 this will
happen:

- ``script.docx`` will be moved to ``~/Documents/DOCX/2018-01/script.docx``
- ``demo.pdf`` will be moved to ``~/Documents/PDF/2016-12/demo.pdf``
- The files will be opened (``open`` command in macOS) from their new location.


Command line interface
----------------------
::

  The file management automation tool.

  Usage:
      organize sim [--config-file=<path>]
      organize run [--config-file=<path>]
      organize config [--open-folder | --path | --debug] [--config-file=<path>]
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
      -d, --debug        Debug your configuration file.

  Full documentation: https://organize.readthedocs.io
