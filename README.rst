.. image:: /docs/images/organize.svg

organize
========
.. image:: https://readthedocs.org/projects/organize/badge/?version=latest
  :target: http://organize.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

*Warning: This project is currently not yet usable. Work is in
progress!*

The file management automation tool.
Install with ``pip install organize-tool`` (Python 3+ only).


Why you might find this useful
------------------------------
Your desktop is a mess? You cannot find anything in your downloads and
documents? Sorting and renaming all these files by hand is too tedious?
Time to automate it once and benefit from it forever.

The following yaml code goes into a file named `config.yaml` in the folder
shown with ``$ organize config``:

- `config.yaml`:

  .. code:: yaml

      rules:
        - folders: '~/Desktop'
          filters:
            - FileExtension:
                - png
                - jpg
            - OlderThan: {years: 1}
          actions:
            - Trash

``$ organize run`` will now move all PNGs and JPGs older than one year from your
desktop into the trash. It is that easy.

Feeling insecure? Run ``$ organize sim`` to see what would happen without
touching your files.

But there is more. You want to move files, use custom
shell scripts or match filenames with regular expressions?
`organize` has you covered. You can even use template strings and extract
information from your files.

Have a look at the full documentation at organize.readthedocs.io.


Command line interface
----------------------
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
