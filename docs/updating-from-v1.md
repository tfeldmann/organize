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
- REMOVED: The exclamation mark exlucde syntax (`! ~/Desktop/exclude`).
  See [Location options](locations.md#location-options).
- All keys (filter names, action names, option names) now must be lowercase.

## Placeholders

organize v2 uses the Jinja template engine. You may need to change some of your
placeholders.

- `{basedir}` is no longer available.
- You have to replace undocumented placeholders like this:

```python
{created.year}-{created.month:02}-{created.day:02}
```

With this:

```python
{created.strftime('%Y-%m-%d')}
```

If you need to left pad other numbers you can now use the following syntax:

```python
{ "{:02}".format(your_variable) }
# or
{ '%02d' % your_variable }
```

## Filters

- [`filename`](filters.md#name) is renamed to `name`.
- [`filesize`](filters.md#size) is renamed to `size`.
- [`created`](filters.md#created) no longer accepts a timezone and uses the local timezone by default.
- [`lastmodified`](filters.md#lastmodified) no longer accepts a timezone and uses the local timezone by default.

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
          rename_template: "{name}-{:02}.format(counter){extension}"
```

If you used `move`, `copy` or `rename` without arguments, nothing changes for you.

That's it. Again, feel free to open a issue if you have trouble migrating your config.
