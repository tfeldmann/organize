Quickstart
==========

Installation
------------
Requirements: Python 3.3+

`organize` is installed via pip:

- ``$ pip install organize-tool`` (or ``$ pip3 install organize-tool``)


Creating your first config file
-------------------------------
To edit the configuration in your $EDITOR, run:

  ``$ organize config``

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

.. note::
  You can run ``$ organize config --path`` to show the full path to the configuration file.


Simulate and run
----------------
After you saved the configuration file, run ``$ organize sim`` to show a simulation of how your files would be organized.

If you like what you see, run ``$ organize run`` to organize your files.

.. note::
  Congrats! You just automated some tedious cleaning tasks!
  Continue to :ref:`Configuration` to see the full potential of organize or skip
  directly to the :ref:`Filters` and :ref:`Actions`.
