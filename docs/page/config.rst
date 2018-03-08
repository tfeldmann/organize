.. _configuration:

*************
Configuration
*************


Editing the configuration
=========================
All configuration takes place in your `config.yaml` file.

- To show the full path to your configuration file:::

    $ organize config --path

- To open the folder containing the configuration file:::

    $ organize config --open-folder

- To edit your configuration in ``$EDITOR`` run:::

    $ organize config


Rule syntax
===========
The rule configuration is done in `YAML <https://learnxinyminutes.com/docs/yaml/>`_.
You need a top-level element ``rules`` which contains a list of rules.
Each rule defines ``folders``, ``filters`` (optional) and ``actions``.

.. code-block:: yaml
  :caption: config.yaml
  :emphasize-lines: 1,2,5,10,14,16,18

  rules:
    - folders:
        - ~/Desktop
        - /some/folder/
      filters:
        - LastModified:
            days: 40
            mode: newer
        - Extension: pdf
      actions:
        - Move: ~/Desktop/Target/
        - Trash

    - folders:
        - ~/Inbox
      filters:
        - Extension: pdf
      actions:
        - Move: ~/otherinbox

- ``folders`` is a list of folders you want to organize.
- ``filters`` is a list of filters to apply to the files - you can filter by file extension, last modified date, regular expressions and many more. See :ref:`Filters`.
- ``actions`` is a list of actions to apply to the filtered files. You can put them into the trash, move them into another folder and many more. See :ref:`Actions`.

.. note::
   At the moment organize only handles the files at the top level of the folders given in ``folders``.
   Recursion through subdirs is planned for later versions.


Folder syntax
=============
Every rule in your configuration file needs to know the folders it applies to.
The easiest way is to define the rules like this:

.. code-block:: yaml
  :caption: config.yaml

  rules:
    - folders:
        - /path/one
        - /path/two
      filters: ...
      actions: ...

    - folders:
        - /path/one
        - /another/path
      filters: ...
      actions: ...


Advanced: Aliases
-----------------------------
Instead of repeating the same folders in each and every rule you can use an alias for multiple folders which you can then reference in each rule.
Aliases are a standard feature of the YAML syntax.

.. code-block:: yaml
  :caption: config.yaml


  all_my_messy_folders: &all
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
  :caption: config.yaml

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


Filter syntax
=============



Action syntax
=============
- Actions with / without parameters
- Using placeholders
