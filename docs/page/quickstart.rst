.. _quickstart:

Quickstart
==========

Installation
------------
Requirements: Python 3.3+

`organize` is installed via pip:

- ``$ pip install organize-tool``

Run the script with:

``$ organize``


Creating your first config file
-------------------------------
To edit the configuration in your $EDITOR, run:

    $ organize config

For example your configuration file could look like this:

.. code-block:: yaml

    rules:
      - folders:
          - ~/Desktop
          - ~/Documents
        filters:
          - LastModified:
              days: 365
        actions:
          - Echo: 'Found old file: {path}'

      - folders:
          - ~/Desktop
        filters:
          - Filename:
              startswith: '_'
        actions:
          - Trash


Simulate and run
----------------
After you created the configuration file, run `organize` with ``$ organize run``. It will print a list of files from
your desktop and documents which are older than one month.
