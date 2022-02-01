# Locations

**Locations** are the folders in which organize searches for resources.
You can set multiple locations for each rule if you want.

A minimum location definition is just a path where to look for files / folders:

```yml
rules:
  - name: "Single location"
    locations: ~/Desktop
    actions: ...
```

If you want to handle multiple locations in a rule, create a list:

```yaml
rules:
  - name: "Location list"
    locations:
      - ~/Desktop
      - /usr/bin/
      - "%PROGRAMDATA%/test"
    actions: ...
```

Using options:

```yaml
rules:
  - name: "Location list"
    locations:
      - path: "~/Desktop"
        max_depth: 3
    actions: ...
```

Note that you can use environment variables in your locations.

## Location options

```yaml
rules:
  - locations:
      path: ...
      max_depth: ...
      search: ...
      exclude_files: ...
      exclude_dirs: ...
      system_exlude_files: ...
      system_exclude_dirs: ...
      ignore_errors: ...
      filter: ...
      filter_dirs: ...
      filesystem: ...
```

- **path** (`str`):
- **max_depth** (`int` or `null`):
- **search** (`str`): "depth", "breadth")):
- **exclude_files** (list of `str`):
- **exclude_dirs** (list of `str`):
- **system_exlude_files** (list of `str`):
- **system_exclude_dirs** (list of `str`):
- **ignore_errors** (`bool`):
- **filter** (list of `str`):
- **filter_dirs** (list of `str`):
- **filesystem** (str):

### `filesystem` and `path`



## Relative locations

## Filesystems

      actions: ...

.. note::

- You can use environment variables in your folder names. On windows this means you can use `%public%/Desktop`, `%APPDATA%`, `%PROGRAMDATA%` etc.
