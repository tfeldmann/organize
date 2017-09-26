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

You can find your config.yaml file location with the command ``organize config``

Example ``config.yaml``:

.. code:: yaml

    folders: &all
      - '~/Desktop/__Inbox__'
      - '~/Download'
      - '~/TF Cloud/Office/_EINGANG_'

    rules:
      # German VDI Nachrichten
      - filters:
        - PaperVdi
        actions:
        - Move: {dest: '~/Documents/VDI Nachrichten/VDI {year}-{month:02}-{day:02}.pdf'}
        folders: *all

      # Matches filename by regular expression
      - filters:
        - Regex: {expr: '^RG(\d{12})-sig\.pdf$'}
        actions:
        - Move: {dest: '~/TF Cloud/Office/Rechnungen/MCF 1und1'}
        folders: *all

      # 1und1 invoices
      - filters:
        - Invoice1and1
        actions:
        - Move: {dest: '~/TF Cloud/Office/Rechnungen/{year}-{month:02}-{day:02} 1und1.pdf'}
        folders: *all
