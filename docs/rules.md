# Rules

A organize config file can be written in [YAML](https://learnxinyminutes.com/docs/yaml/)
or [JSON](https://learnxinyminutes.com/docs/json/). See [configuration](configuration.md)
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

```yml
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
    tags: ...

  # Another rule
  - name: ...
    enabled: ...
    # ... and so on
```

The rule options in detail:

- **name** (`str`): The rule name
- **enabled** (`bool`): Whether the rule is enabled / disabled _(Default: `true`)_
- **targets** (`str`): `"dirs"` or `"files"` _(Default: `"files"`)_
- **locations** (`str`|`list`) - A single location string or list of [locations](locations.md)
- **subfolders** (`bool`): Whether to recurse into subfolders of all locations _(Default: `false`)_
- **filter_mode** (`str`): `"all"`, `"any"` or `"none"` of the filters must apply _(Default: `"all"`)_
- **filters** (`list`): A list of [filters](filters.md) _(Default: `[]`)_
- **actions** (`list`): A list of [actions](actions.md)
- **tags** (`list`): A list of [tags](configuration.md#running-specific-rules-of-your-config)

## Targeting directories

When `targets` is set to `dirs`, organize will work on the folders, not on files.

The filters adjust their meaning automatically. For example the `size` filter sums up
the size of all files contained in the given folder instead of returning the size of a
single file.

Of course other filters like `exif` or `filecontent` do not work on folders and will
return an error.

## Templates and placeholders

Placeholder variables are used with curly braces `{var}`.

These variables are **always available**:

`{env}` (`dict`)<br>
All your environment variables. You can access individual env vars like this: `{env.MY_VARIABLE}`.

`{path}` ([`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#methods-and-properties))<br>
The full path to the current file / folder on the local harddrive.
This is not available for remote locations - in this case use `fs` and `fs_path`.

`{relative_path}` (`str`)<br>
the relative path of the current file or dir.

`{now}` (`datetime`)<br>
The current datetime in the local timezone.

`{utcnow}` (`datetime`)<br>
The current UTC datetime.

In addition to that nearly all filters add new placeholders with information about
the currently handled file / folder.

Example on how to access the size and hash of a file:

```yaml
rules:
  - locations: ~/Desktop
    filters:
      - size
      - hash
    actions:
      - echo: "{size} {hash}"
```

!!! note

    In order to use a value returned by a filter it must be listed in the filters!

## Advanced: Aliases

Instead of repeating the same locations / actions / filters in each and every rule you
can use an alias for multiple locations which you can then reference in each rule.

Aliases are a standard feature of the YAML syntax.

```yml
all_my_messy_folders: &all
  - ~/Desktop
  - ~/Downloads
  - ~/Documents
  - ~/Dropbox

rules:
  - locations: *all
    filters: ...
    actions: ...

  - locations: *all
    filters: ...
    actions: ...
```

You can even use multiple folder lists:

```yml
private_folders: &private
  - "/path/private"
  - "~/path/private"

work_folders: &work
  - "/path/work"
  - "~/My work folder"

all_folders: &all
  - *private
  - *work

rules:
  - locations: *private
    filters: ...
    actions: ...

  - locations: *work
    filters: ...
    actions: ...

  - locations: *all
    filters: ...
    actions: ...

  # same as *all
  - locations:
      - *work
      - *private
    filters: ...
    actions: ...
```
