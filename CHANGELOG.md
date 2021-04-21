# Changelog

## v1.10.1 (2021-04-21)
- Action `macos_tags` now supports colors and placeholders.
- Show full expanded path if folder is not found.

## v1.10.0 (2021-04-20)
- Add filter `mimetype`
- Add action `macos_tags`
- Support [`simplematch`](https://github.com/tfeldmann/simplematch) syntax in
  `filename`-filter. 
- Updated dependencies
- Because installing `textract` is quite hard on some platforms it is now an optional
  dependency. Install it with `pip install organize-tool[textract]`
- This version needs python 3.6 minimum. Some dependencies that were simply backports
  (pathlib2, typing) are removed.
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
  of environment variables
- Added `years`, `months`, `weeks` and `seconds` parameter to filter `created` and 
  `lastmodified`

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
  and additionally `%name%` on windows).
  For example this allows the usage of e.g. `%public/Desktop%` in windows.

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
- Fixes a bug with command line arguments in the ``$EDITOR`` environment
  variable.
- Fixes a bug where an empty config wouldn't show the correct error message.
- Fix binary wheel creation in setup.py by using environment markers

## v1.4.1 (2018-10-05)
- A custom separator ``counter_separator`` can now be set in the actions Move,
  Copy and Rename.

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
  returns `'png'` instead of `'.png'`.

## v1.0 (2018-03-13)
- Initial release.
