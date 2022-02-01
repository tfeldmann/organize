# Rules

A organize config file can be written in [YAML](https://learnxinyminutes.com/docs/yaml/)
or [JSON](https://learnxinyminutes.com/docs/json/). See [configuration](00-configuration.md)
on how to locate your config file.

The top level element must be a dict with a key "rules".
"rules" contains a list of objects with the required keys "locations" and "actions".

A minimum config:

```yaml
rules:
  - locations: "~/Desktop"
    actions:
      - echo: "Hello World!"
```

Organize checks your rules from top to bottom. For every resource in each location (top to bottom)
it will check whether the filters apply (top to bottom) and then execute the given actions (top to bottom).

So with this minimal configuration it will print "Hello World!" for each file it finds in your Desktop.

## Rule options

```yaml
rules:
  # First rule
  - name: ...
    enabled: ...
    targets: ...
    locations: ...
    subfolders: ...
    filter_mode: ...
    filters: ...
    actions: ...

  # Another rule
  - name: ...
    enabled: ...
    # ... and so on
```

The rule options in detail:

- **name** (`str`): The rule name
- **enabled** (`bool`): Whether the rule is enabled / disabled _(Default: `true`)_
- **targets** (`str`): `"dirs"` or `"files"` _(Default: `"files"`)_
- **locations** (`str`|`list`) - A single location string or list of [locations](02-locations.md)
- **subfolders** (`bool`): Whether to recurse into subfolders of all locations _(Default: `false`)_
- **filter_mode** (`str`): `"all"`, `"any"` or `"none"` of the filters must apply _(Default: `"all"`)_
- **filters** (`list`): A list of [filters](03-filters.md) _(Default: `[]`)_
- **actions** (`list`): A list of [actions](04-actions.md)

## Templates and placeholders

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


## Advanced: Aliases

Instead of repeating the same folders in each and every rule you can use an alias for multiple folders which you can then reference in each rule.
Aliases are a standard feature of the YAML syntax.

.. code-block:: yaml
all_my_messy_folders: &all - ~/Desktop - ~/Downloads - ~/Documents - ~/Dropbox

rules: - folders: \*all
filters: ...
actions: ...

    - folders: *all
      filters: ...
      actions: ...

You can even use multiple folder lists:

.. code-block:: yaml
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
