.. _configuration:

*************
Configuration
*************


Creating a config file
======================
All configuration takes place in your `config.yaml` file. You can find your config
folder by executing ``$ organize config``.


Folder syntax
=============
Every rule in your configuration file needs to know the folders it applies to.
The easiest way is to define the rules like this:

.. code-block:: yaml

    rules:
      - folders:
          - '/path/one'
          - '/path/two'
        filters: ...
        actions: ...

      - folders:
          - '/path/one'
          - '/another/path'
        filters: ...
        actions: ...


Advanced: Folder lists
----------------------

Instead of repeating the same folders in each and every rule you can use folder lists which you can reference in each rule.
Referencing is a standard feature of the YAML syntax.

.. code-block:: yaml

    all_folders: &all
      - '/path/one'
      - '/path/two'
      - '/path/three'

    rules:
      - folders: *all
        filters: ...
        actions: ...

      - folders: *all
        filters: ...
        actions: ...

You can even use multiple folder lists:

.. code-block:: yaml

    private_folders: &private
      - '/path/private'
      - '~/path/private'

    work_folders: &work
      - '/path/work'
      - '~/My work folder'

    all_folders: &all
      - *private
      - *work

    rules:
      - folders: *private
        filters: ...
        actions: ...

      - folders: *work
        filters: ...
        actions: ...

      - folders: *all
        filters: ...
        actions: ...

      # same as *all
      - folders:
          - *work
          - *private
        filters: ...
        actions: ...


Rule syntax
===========
- Basic rule syntax
- filter_mode


Filter syntax
=============
- Filter with/without parameters


Action syntax
=============
- Actions with / without parameters
- Using placeholders
