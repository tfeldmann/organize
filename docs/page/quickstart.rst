Quickstart
==========

Installation
------------
Requirements: Python 3.6+

`organize` is installed via pip:

``$ pip install organize-tool``

If you want all the text extraction capabilities, install with `textract` like this:

``$ pip3 -U "organize-tool[textract]"``


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
          - filename:
              startswith: Screen Shot
        actions:
          - move: ~/Desktop/Screenshots/

      # move incomplete downloads older > 30 days into the trash
      - folders:
          - ~/Downloads
        filters:
          - extension:
              - crdownload
              - part
              - download
          - lastmodified:
              days: 30
        actions:
          - trash

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
