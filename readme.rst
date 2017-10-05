organize
========

*Warning: This project is currently not yet usable. Work is in
progress!*

The file management automation tool.

``organize`` is a file organizer for the command line. It automatically
organizes your files according to your rules.

Usage
-----

::

    Usage:
        organize sim
        organize run
        organize config
        organize list
        organize --help
        organize --version

    Arguments:
        sim             Simulate organizing your files. This allows you to check your rules.
        run             Organizes your files according to your rules.
        config          Open the organize config folder
        list            List available filters and actions

    Options:
        --version       Show program version and exit.
        -h, --help      Show this screen and exit.

Example config
--------------
(This goes into a file named `config.yaml` in the folder shown with
``organize config``.)

.. code:: yaml

    rules:
      - folders: '~/Desktop'
      - filters:
          - FileExtension:
              - png
              - jpg
          - OlderThan: {years: 1}
      - actions:
          - Trash

``$ organize run`` will now move all PNGs and JPGs older than one year from your
desktop into the trash. It is that easy.

Feeling insecure? Run ``$ organize sim`` to see what would happen without
touching your files.

But there is more. You want to use custom shell scripts, move files with
template strings or use regexes?
`organize` has you covered -- just have a look at the documentation at organize.readthedocs.io.
