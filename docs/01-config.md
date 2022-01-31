# Configuration

## Editing the configuration

organize has a default config file if no other file is given.

To edit the default configuration file:

```sh
$ organize edit  # opens in $EDITOR
$ organize edit --editor=vim
$ EDITOR=code organize edit
```

To open the folder containing the configuration file:

```sh
$ organize reveal
$ organize reveal --path  # show the full path to the default config
```

To debug your configuration run:

```sh
$ organize check
```

## Configuration basics

## Environment variables

- `EDITOR` - The editor used to edit the config file.
- `ORGANIZE_CONFIG` - The path to the default config file.
- `NO_COLOR` - if this is set, the output is not colored.

## Rule syntax

The rule configuration is done in [YAML](https://learnxinyminutes.com/docs/yaml/).
You need a top-level element `rules` which contains a list of rules.
Each rule defines `folders`, `filters` (optional) and `actions`.

```yaml
rules:
- folders:
    - ~/Desktop
    - /some/folder/
  filters:
    - lastmodified:
        days: 40
        mode: newer - extension: pdf
  actions:
    - move: ~/Desktop/Target/ - trash

  - folders:
    - ~/Inbox
    filters:
      - extension: pdf
    actions:
      - move: ~/otherinbox
```

- `folders` is a list of folders you want to organize.
- `filters` is a list of filters to apply to the files - you can filter by file extension, last modified date, regular expressions and many more. See :ref:`Filters`.
- `actions` is a list of actions to apply to the filtered files. You can put them into the trash, move them into another folder and many more. See :ref:`Actions`.

Other optional per rule settings:

- `enabled` can be used to temporarily disable single rules. Default = true
- `subfolders` specifies whether subfolders should be included in the search. Default = false. This setting only applies to folders without glob wildcards.
- `system_files` specifies whether to include system files (desktop.ini, thumbs.db, .DS_Store) in the search. Default = false

## Folder syntax

Every rule in your configuration file needs to know the folders it applies to.
The easiest way is to define the rules like this:

.. code-block:: yaml
:caption: config.yaml

rules: - folders: - /path/one - /path/two
filters: ...
actions: ...

    - folders:
        - /path/one
        - /another/path
      filters: ...
      actions: ...

.. note::

- You can use environment variables in your folder names. On windows this means you can use `%public%/Desktop`, `%APPDATA%`, `%PROGRAMDATA%` etc.

### Globstrings

You can use globstrings in the folder lists. For example to get all files with filenames ending with `_ui` and any file extension you can use:

.. code-block:: yaml
:caption: config.yaml

rules: - folders: - '~/Downloads/_\_ui._'
actions: - echo: '{path}'

You can use globstrings to recurse through subdirectories (alternatively you can use the `subfolders: true` setting as shown below)

.. code-block:: yaml
:caption: config.yaml

rules: - folders: - '~/Downloads/\*_/_.\*'
actions: - echo: 'base {basedir}, path {path}, relative: {relative_path}'

    # alternative syntax
    - folders:
        - ~/Downloads
      subfolders: true
      actions:
        - echo: 'base {basedir}, path {path}, relative: {relative_path}'

The following example recurses through all subdirectories in your downloads folder and finds files with ending in `.c` and `.h`.

.. code-block:: yaml
:caption: config.yaml

rules: - folders: - '~/Downloads/\*_/_.[c|h]'
actions: - echo: '{path}'

.. note::

- You have to target files with the globstring, not folders. So to scan through all folders starting with \_log\__ you would write `yourpath/log\_\_/_`

### Excluding files and folders

Files and folders can be excluded by prepending an exclamation mark. The following example selects all files
in `~/Downloads` and its subfolders - excluding the folder `Software`:

.. code-block:: yaml
:caption: config.yaml

rules: - folders: - '~/Downloads/\*_/_' - '! ~/Downloads/Software'
actions: - echo: '{path}'

Globstrings can be used to exclude only specific files / folders. This example:

- adds all files in `~/Downloads`
- exludes files from that list whose name contains the word `system` ending in `.bak`
- adds all files from `~/Documents`
- excludes the file `~/Documents/important.txt`.

.. code-block:: yaml
:caption: config.yaml

rules: - folders: - '~/Downloads/**/\*' - '! ~/Downloads/**/_system_.bak' - '~/Documents' - '! ~/Documents/important.txt'
actions: - echo: '{path}'

.. note::

- Files and folders are included and excluded in the order you specify them!
- Please make sure your are putting the exclamation mark within quotation marks.

### Aliases

Instead of repeating the same folders in each and every rule you can use an alias for multiple folders which you can then reference in each rule.
Aliases are a standard feature of the YAML syntax.

.. code-block:: yaml
:caption: config.yaml

all_my_messy_folders: &all - ~/Desktop - ~/Downloads - ~/Documents - ~/Dropbox

rules: - folders: \*all
filters: ...
actions: ...

    - folders: *all
      filters: ...
      actions: ...

You can even use multiple folder lists:

.. code-block:: yaml
:caption: config.yaml

private_folders: &private - '/path/private' - '~/path/private'

work_folders: &work - '/path/work' - '~/My work folder'

all_folders: &all - *private - *work

rules: - folders: \*private
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

## Filter syntax

`filters` is a list of :ref:`Filters`.
Filters are defined like this:

.. code-block:: yaml
:caption: config.yaml

rules: - folders: ...
actions: ...
filters: # filter without parameters - FilterName

        # filter with a single parameter
        - FilterName: parameter

        # filter expecting a list as parameter
        - FilterName:
          - first
          - second
          - third

        # filter with multiple parameters
        - FilterName:
            parameter1: true
            option2: 10.51
            third_argument: test string

.. note::
Every filter comes with multiple usage examples which should be easy to adapt for your use case!

## Action syntax

`actions` is a list of :ref:`Actions`.
Actions can be defined like this:

.. code-block:: yaml
:caption: config.yaml

rules: - folders: ...
actions: # action without parameters - ActionName

        # action with a single parameter
        - ActionName: parameter

        # filter with multiple parameters
        - ActionName:
            parameter1: true
            option2: 10.51
            third_argument: test string

.. note::
Every action comes with multiple usage examples which should be easy to adapt for your use case!

### Variable substitution (placeholders)

**You can use placeholder variables in your actions.**

Placeholder variables are used with curly braces `{var}`.
You always have access to the variables `{path}`, `{basedir}` and `{relative_path}`:

- `{path}` -- is the full path to the current file
- `{basedir}` -- the current base folder (the base folder is the folder you
  specify in your configuration).
- `{relative_path}` -- the relative path from `{basedir}` to `{path}`

Use the dot notation to access properties of `{path}`, `{basedir}` and `{relative_path}`:

- `{path}` -- the full path to the current file
- `{path.name}` -- the full filename including extension
- `{path.stem}` -- just the file name without extension
- `{path.suffix}` -- the file extension
- `{path.parent}` -- the parent folder of the current file
- `{path.parent.parent}` -- parent calls are chainable...

- `{basedir}` -- the full path to the current base folder
- `{basedir.parent}` -- the full path to the base folder's parent

and any other property of the python `pathlib.Path` (`official documentation <https://docs.python.org/3/library/pathlib.html#methods-and-properties>`\_) object.

Additionally :ref:`Filters` may emit placeholder variables when applied to a
path. Check the documentation and examples of the filter to see available
placeholder variables and usage examples.

Some examples include:

- `{lastmodified.year}` -- the year the file was last modified
- `{regex.yournamedgroup}` -- anything you can extract via regular expressions
- `{extension.upper}` -- the file extension in uppercase
- ... and many more.
