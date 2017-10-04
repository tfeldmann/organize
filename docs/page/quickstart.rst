Quickstart
==========

Installation
------------

`organize` is installed via pip

- ``$ pip install organize``

(`organize` is Python 3 only.)


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
          - Echo: {msg: 'Found old file: {path}'}


Simulate and run
----------------
After you created the configuration file, run `organize` with ``$ organize run``. It will print a list of files from
your desktop and documents which are older than one month.


List installed actions and filters
----------------------------------
