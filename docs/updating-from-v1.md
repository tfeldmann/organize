# Updating from organize v1.x

First of all, thank you for being a long time user of `organize`!

I tried to keep the amount of breaking changes small but could not avoid them
completely. Feel free to pin organize to v1.x, but then you're missing the party.

Please open a issue on Github if you need help migrating your config file!

## Config

- `folders` must be renamed to `locations`.
- REMOVED: The glob syntax (`/Docs/**/*.png`)
- REMOVED: The exclamation mark exlucde syntax (`! ~/Desktop/exclude`)

With `locations`, there are now much better options in place.
Please change your `folders` definition to the `locations` definition: [Locations documentation](locations.md).

- All keys (filter names, action names, option names) now must be lowercase.

## Placeholders

organize v2 uses the Jinja template engine. You may need to change some of your placeholders.

- `{basedir}` is no longer available.
- Replace undocumented placeholders like this:

  ```py
  {created.year}-{created.month:02}-{created.day:02}
  ```

  With this:

  ```py
  {created.strftime('%Y-%m-%d')}
  ```

## Filters

- [`filename`](filters.md#name) is renamed to `name`.
- [`filesize`](filters.md#size) is renamed to `size`.
- [`created`](filters.md#created) no longer accepts a timezone and uses the local timezone by default.
- [`lastmodified`](filters.md#lastmodified) no longer accepts a timezone and uses the local timezone by default.

## Actions

- [`copy`](actions.md#copy) arguments changed to support conflict resolution options.
- [`move`](actions.md#move) arguments changed to support conflict resolution options.
- [`rename`](actions.md#rename) arguments changed to support conflict resolution options.
