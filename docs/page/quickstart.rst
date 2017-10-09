.. _quickstart:

Quickstart
==========

Installation
------------
Requirements: Python 3+

`organize` is installed via pip:

- ``$ pip install organize-tool``


Creating your first config file
-------------------------------
To print the standard location for organize's config file, use the config command in your terminal (This will also open the path in your file manager)::

    $ organize config

And create a file named `config.yaml` with the content:

.. code-block:: yaml

    rules:
      - folders:
          - '~/Desktop'
          - '~/Documents'
        filters:
          - OlderThan: {months: 1}
        actions:
          - Echo: 'Found old file: {path}'


Simulate and run
----------------
After you created the configuration file, run `organize` with ``$ organize run``. It will print a list of files from
your desktop and documents which are older than one month.
