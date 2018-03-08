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
  :caption: config.yaml

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
            - crdownload
            - part
            - download
          - LastModified:
            days: 30
        actions:
          - Trash


Simulate and run
----------------
After you created the configuration file, run `organize` with ``$ organize run``. It will print a list of files from
your desktop and documents which are older than one month.
