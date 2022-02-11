# Updating from organize v1.x

First of all, thank you for being a long time user of `organize`!

I tried to keep the amount of breaking changes small but could not avoid them
completely. Feel free to pin organize to v1.x, but then you're missing the party.

Please open a issue on Github if you need help migrating your config file!

## Folders

Folders have become [Locations](locations.md) in organize v2.

- `folders` must be renamed to `locations` in your config.
- REMOVED: The glob syntax (`/Docs/**/*.png`).
  See [Location options](locations.md#location-options).
- REMOVED: The exclamation mark exclude syntax (`! ~/Desktop/exclude`).
  See [Location options](locations.md#location-options).
- All keys (filter names, action names, option names) now must be lowercase.

## Placeholders

organize v2 uses the Jinja template engine. You may need to change some of your
placeholders.

- `{basedir}` is no longer available.
- You have to replace undocumented placeholders like this:

```yaml
"{created.year}-{created.month:02}-{created.day:02}"
```

With this:

```yaml
"{created.strftime('%Y-%m-%d')}"
```

If you need to left pad other numbers you can now use the following syntax:

```yaml
"{'%02d' % your_variable}"
# or
"{ '{:02}'.format(your_variable) }"
```

## Filters

- [`filename`](filters.md#name) is renamed to `name`.
- [`filesize`](filters.md#size) is renamed to `size`.
- [`created`](filters.md#created) no longer accepts a timezone and uses the local timezone by default.
- [`lastmodified`](filters.md#lastmodified) no longer accepts a timezone and uses the local timezone by default.
- [`extension`](filters.md#extension) `lower` and `upper` are now functions and must be called like this:
  `"{extension.upper()}"` and `"{extension.lower()}"`.

## Actions

The copy, move and rename actions got a whole lot more powerful. You now have several
conflict options and can specify exactly how a file should be renamed in case of a
conflict.

This means you might need to change your config to use the new parameters.

- [`copy`](actions.md#copy) arguments changed to support conflict resolution options.
- [`move`](actions.md#move) arguments changed to support conflict resolution options.
- [`rename`](actions.md#rename) arguments changed to support conflict resolution options.

Example:

```yml
rules:
  - folders: ~/Desktop
    filters:
      - extension: pdf
    actions:
      - move:
          dest: ~/Documents/PDFs/
          overwrite: false
          counter_seperator: "-"
```

becomes (organize v2):

```yaml
rules:
  - locations: ~/Desktop
    filters:
      - extension: pdf
    actions:
      - move:
          dest: ~/Documents/PDFs/
          on_conflict: rename_new
          rename_template: "{name}-{counter}{extension}"
```

If you used `move`, `copy` or `rename` without arguments, nothing changes for you.

## Settings

The `system_files` setting has been removed. In order to include system files in your
search, overwrite the default [`system_exclude_files`](locations.md#location-options)
with an empty list:

```yaml
rules:
  - locations:
      - path: ~/Desktop/
        system_exclude_files: []
        system_exclude_dirs: []
    filters:
      - name: .DS_Store
    actions:
      - trash
```

That's it. Again, feel free to open a issue if you have trouble migrating your config.
