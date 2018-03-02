.. image:: /docs/images/organize.svg

organize
========
.. image:: https://readthedocs.org/projects/organize/badge/?version=latest
  :target: https://organize.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://travis-ci.org/tfeldmann/organize.svg?branch=master
    :target: https://travis-ci.org/tfeldmann/organize

**The file management automation tool.**

`organize` is installed via pip (requirement: Python 3.3+):

- ``$ pip3 install organize-tool``

Run the script with:

``$ organize``


Why you might find this useful
------------------------------
Your desktop is a mess? You cannot find anything in your downloads and
documents? Sorting and renaming all these files by hand is too tedious?
**Time to automate it once and benefit from it forever**.

The following yaml code goes into a file named `config.yaml` in the folder
shown with ``$ organize config``:

- `config.yaml`:

  .. code:: yaml

      rules:
        - folders:
            - ~/Desktop
            - ~/Downloads
          filters:
            - Extension:
                - png
                - jpg
            - LastModified:
                days: 365
          actions:
            - Trash

``$ organize run`` will now move all PNGs and JPGs older than one year from your
desktop and downloads folder into the trash. It is that easy.

Feeling insecure? Run ``$ organize sim`` to see what would happen without
touching your files.

But there is more. You want to move files, use custom
shell scripts or match filenames with regular expressions?
`organize` has you covered. You can even use template strings and extract
information from your files.

Have a look at the full documentation at https://organize.readthedocs.io/.


Functionality
-------------

*Filters* (how to select files):

 - File extension
 - Regular expression
 - Last modified date
 - Filename

*Actions* (what you can with your files):

 - Move files
 - Copy files
 - Rename files in place
 - Run shell command
 - Run inline Python code
 - Move into Trash
 - Print something to the console

If you miss a feature please file an issue. Pull requests are very welcome!


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
      sim             Simulate organizing your files. This allows you to check your rules.
      run             Organizes your files according to your rules.
      config          Open the configuration file in $EDITOR.
      list            List available filters and actions.
      --version       Show program version and exit.
      -h, --help      Show this screen and exit.

  organize config options:
      -o, --open-folder  Open the folder containing the configuration files.
      -p, --path         Show the path of the configuration file.
      -d, --debug        Print the current configuration for debugging purposes.
