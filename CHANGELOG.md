# Changelog

## v2.0.0 - WIP

This is a huge update with lots of improvements.
Please backup all your important stuff before running and use the simulate option!

[**Migration Guide**](docs/updating-from-v1.md)

### what's new

- You can now [target directories](docs/rules.md#targeting-directories) with your rules
  (copying, renaming, etc a whole folder)
- [Organize inside or between (S)FTP, S3 Buckets, Zip archives and many more](docs/locations.md#remote-filesystems-and-archives)
  (list of [available filesystems](https://www.pyfilesystem.org/page/index-of-filesystems/)).
- [`max_depth`](docs/locations.md#location-options) setting when recursing into subfolders
- Respects your rule order - safer, less magic, less surprises.
  - (organize v1 tried to be clever. v2 now works your config file from top to bottom)
- [Jinja2 template engine for placeholders](docs/rules.md#templates-and-placeholders).
- Instant start. (does not need to gather all the files before starting)
- [Filters can now be excluded](docs/filters.md#how-to-exclude-filters).
- [Filter modes](docs/rules.md#rule-options): `all`, `any` and `none`.
- [Rule names](docs/rules.md#rule-options).
- new conflict resolution settings in [`move`](docs/actions.md#move),
  [`copy`](docs/actions.md#copy) and [`rename`](docs/actions.md#rename) action:
  - Options are `skip`, `overwrite`, `trash`, `rename_new` or `rename_existing`
  - You can now define a custom `rename_template`.
- The [`python`](docs/actions.md#python) action can now be run in simulation.
- The [`shell`](docs/actions.md#shell) action now returns stdout and errorcode.
- Added filter [`empty`](docs/filters.md#empty) - find empty files and folders
- Added filter [`hash`](docs/filters.md#hash) - generate file hashes
- Added action [`symlink`](docs/actions.md#symlink) - generate symlinks
- Added action [`confirm`](docs/actions.md#confirm) - asks for confirmation
- Many small fixes and improvements!

### changed

- The `timezone` keyword for [`lastmodified`](docs/filters.md#lastmodified) and
  [`created`](docs/filters.md#created) was removed. The timezone is
  now the local timezone by default.
- The `filesize` filter was renamed to [`size`](docs/filters.md#size) and can now be
  used to get directory sizes as well.
- The `filename` filter was renamed to [`name`](docs/filters.md#name) and can now be
  used to get directory names as well.
- The [`size`](docs/filters.md#size) filter now returns multiple formats

### removed

- Glob syntax is gone from folders ([no longer needed](docs/locations.md))
- `"!"` folder exclude syntax is gone ([no longer needed](docs/locations.md))

## v1.10.1 (2021-04-21)

- Action `macos_tags` now supports colors and placeholders.
- Show full expanded path if folder is not found.

## v1.10.0 (2021-04-20)

- Add filter `mimetype`
- Add action `macos_tags`
- Support [`simplematch`](https://github.com/tfeldmann/simplematch) syntax in
  `lename`-filter.
- Updated dependencies
- Because installing `textract` is quite hard on some platforms it is now an optional
  dendency. Install it with `pip install organize-tool[textract]`
- This version needs python 3.6 minimum. Some dependencies that were simply backports
  (thlib2, typing) are removed.
- Add timezones in created and last_modified filters (Thank you, @win0err!)

## v1.9.1 (2020-11-10)

- Add {env} variable
- Add {now} variable

## v1.9 (2020-06-12)

- Add filter `Duplicate`.

## v1.8.2 (2020-04-03)

- Fix a bug in the filename filter config parsing algorithm with digits-only filenames.

## v1.8.1 (2020-03-28)

- Flatten filter and action lists to allow enhanced config file configuration (Thanks to @rawdamedia!)
- Add support for multiline content filters (Thanks to @zor-el!)

## v1.8.0 (2020-03-04)

- Added action `Delete`.
- Added filter `FileContent`.
- Python 3.4 is officially deprecated and no longer supported.
- `--config-file` command line option now supports `~` for user folder and expansion
  oenvironment variables
- Added `years`, `months`, `weeks` and `seconds` parameter to filter `created` and
  `stmodified`

## v1.7.0 (2019-11-26)

- Added filter `Exif` to filter by image exif data.
- Placeholder variable properties are now case insensitve.

## v1.6.2 (2019-11-22)

- Fix `Rename` action (`'PosixPath' object has no attribute 'items'`).
- Use type hints everywhere.

## v1.6.1 (2019-10-25)

- Shows a warning for missing folders instead of raising an exception.

## v1.6 (2019-08-19)

- Added filter: `Python`
- Added filter: `FileSize`
- The organize module can now be run directly: `python3 -m organize`
- Various code simplifications and speedups.
- Fixes an issue with globstring file exclusion.
- Remove `clint` dependency as it is no longer maintained.
- Added various integration tests
- The "~~ SIMULATION ~~"-banner now takes up the whole terminal width

## v1.5.3 (2019-08-01)

- Filename filter now supports lists.

## v1.5.2 (2019-07-29)

- Environment variables in folder pathes are now expanded (syntax `$name` or `${name}`
  a additionally `%name%` on windows).
  F example this allows the usage of e.g. `%public/Desktop%` in windows.

## v1.5.1 (2019-07-23)

- New filter "Created" to filter by creation date.
- Fixes issue #39 where globstrings don't work most of the time.
- Integration test for issue #39
- Support indented config files

## v1.5 (2019-07-17)

- Fixes issue #31 where the {path} variable always resolves to the source path
- Updated dependencies
- Exclude changelog and readme from published wheel

## v1.4.5 (2019-07-03)

- Filter and Actions names are now case-insensitive

## v1.4.4 (2019-07-02)

- Fixes issues #36 with umlauts in config file on windows

## v1.4.3 (2019-06-05)

- Use safe YAML loader to fix a deprecation warning. (Thanks mope1!)
- Better error message if a folder does not exist. (Again thanks mope1!)
- Fix example code in documentation for LastModified filter.
- Custom config file locations (given by cmd line argument or environment variable).
- `config --debug` now shows the full path to the config file.

## v1.4.2 (2018-11-14)

- Fixes a bug with command line arguments in the `$EDITOR` environment
  viable.
- Fixes a bug where an empty config wouldn't show the correct error message.
- Fix binary wheel creation in setup.py by using environment markers

## v1.4.1 (2018-10-05)

- A custom separator `counter_separator` can now be set in the actions Move,
  Cy and Rename.

## v1.4 (2018-09-21)

- Fixes a bug where glob wildcards are not detected correctly
- Adds support for excluding folders and files via glob syntax.
- Makes sure that files are only handled once per rule.

## v1.3 (2018-07-06)

- Glob support in folder configuration.
- New variable {relative_path} is now available in actions.

## v1.2 (2018-03-19)

- Shows the relative path to files in subfolders.

## v1.1 (2018-03-13)

- Removes the colon from extension filter output so `{extension.lower}` now
  rurns `'png'` instead of `'.png'`.

## v1.0 (2018-03-13)

- Initial release.
