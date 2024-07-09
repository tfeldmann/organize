# Changelog

## [Unreleased]

## v3.2.5 (2024-07-09)

- Fixes a bug where some location options did not accept yaml aliases
  (#390, thanks for reporting @zany130).

## v3.2.4 (2024-07-07)

- Fixes a bug preventing organize from starting (thanks @feather42).
- Fixes a bug where ignoring failing shell commands would not work (thanks @florianklumb).

## v3.2.3 (2024-03-28)

- Improves the logic of finding and creating config files.
- Fixes a bug where config files in XDG_CONFIG_HOME are not found (#371).
- Fixes a bug in the `relative_path` parameter crashing on actions after moving files (#372).

## v3.2.2 (2024-03-04)

- Fixes an problem where the `organize new` command fails to create a new config file.

## v3.2.1 (2024-02-23)

- Files and folders are now handled in natural sort order (#354).

## v3.2.0 (2024-02-19)

- Integrated `.docx`, `.pdf` and various raw text parsers into `filecontent` filter.
- Removed `textract` and ~50 MB of dependencies as they are no longer required.
- Full Python 3.12 support
- Add support for piping in a config file from STDIN (`organize run --stdin < file.yml`)

**Important:**

You may have to adjust your `filecontent` regexes. The output should be a bit cleaner
now.

## v3.1.2 (2024-02-16)

- Fixes a validation error where correctly defined actions were not accepted in Python 3.12.2.

## v3.1.1 (2024-02-11)

- Fixes the `organize show` command which broke in v3.1.0.

## v3.1.0 (2024-02-04)

- Add a new output format `errorsonly` which only shows output if an error occured.
- Fixes a bug where messages and paths containing brackets where not printed correctly
  (#348, thanks @kwbr!)

## v3.0.1 (2024-01-12)

- Fixes a bug where Quicktime and mp4 files return no Exif data.
  (#313, @jleatham thanks for debugging!)
- Fixes a bug where `exlude_dirs` are not correctly excluded. (#339)

## v3.0.0 (2024-01-05)

- Supports `exiftool` in the `exif` filter by setting the `ORGANIZE_EXIFTOOL_PATH` env
  var. (thanks to @HernandoR for working on qtff support)
- Fixes the `min_depth` location parameter. (thanks to @danielklim for working on this)

## v3.0.0a2 (2024-01-02)

- Fix bug on first run of `organize new`. Create the organize config directory if it
  does not exist. (thanks @white-gecko)
- Adds action `hardlink`.

## v3.0.0a1 (2024-01-01)

- Default to UTF-8 encoding when reading and writing config files for windows users
  who don't use python in UTF-8 mode (env variable `PYTHONUTF8=1`).
- `write`-action: Allow setting the text encoding.

## v3.0.0a0 (2023-12-31)

- New action: `write` to write lines into a file.
- New filter: `date_lastused` (macOS only).
- You can now specify the timezone in all time based filters.
- Removed hidden (deprecated) CLI option `--config-file`.
- Lots of new tests and some bugfixes.
- `exif` filter now supports the simplematch syntax.
- Placeholder`{now}` must be `{now()}` now.
- Multiple `path`s per location are now supported.
- Locations now support a `min_depth` option
- Duplicate filter: `detect_original_by` now supports `last_seen`.
- New command line interface (added `new`, `show` and `list` commands).
- `JSONL` output (`organize run --format=JSONL`)
- `move` and `copy` now intelligently autodetect if you mean to move to a folder
  (This autodetection can be deactivated).
- `copy` action: You can now specify whether you want to continue with the original
  or with the copy.
- Completely removes the `pyfilesystem` dependency.
- At least a 4x speed up. Often more than 10x.

## v2.4.3 (2023-10-14)

- Modified filter: `exif`. Enabled datetime fields on exif data (Issue #266) (Thanks @FlorianFritz)
- Support Exif data from Huawei and Honer phones (Thanks @HernandoR)

## v2.4.2 (2023-08-25)

- Fix reading exif data for HEIC images (Issue #267)

## v2.4.1 (2023-08-25)

- Fix unicode bug in logging (Issue #294) (Thanks @xdhmoore)
- Updated dependencies (Thanks @gaby)
- Removed support for python 3.7 (EOL - June 2023) (Thanks @gaby)

## v2.4.0 (2022-09-05)

- New action: `write`.
- New filter: `date_lastused` (macOS only).
- Conflict resolution renaming now starts with 2 instead of 1.
- Add support for FS urls as path to the config file and working dir
  (both in the CLI and ORGANIZE_CONFIG environment variable).
- Removed hidden (deprecated) CLI option `--config-file`.
- Lots of new tests and some bugfixes.

## v2.3.0 (2022-07-26)

- New filter: `macos_tags` (macOS only).
- Ignore broken symlinks (Issue #202)

## v2.2.0 (2022-03-31)

- Tag support (#199) to run subsets of rules in your config.

## v2.1.2 (2022-02-13)

- Hotfix for `filecontent` filter.

## v2.1.1 (2022-02-13)

- `filecontent` filter: Fixes bug #188.
- Bugfix for #185 and #184.

## v2.1.0 (2022-02-11)

- Added filter `date_added` (macOS only)
- `created` filter now supports gnu coreutils stat utility for birthtime detection
- refactored time based filters into a common class

## v2.0.9 (2022-02-10)

- `shell` shows a message when code is not run in simulation
- `shell` add options `simulation_output` and `simulation_returncode`
- fixes a bug where location options are applied to other locations as well
- `created` filter now falls back to using the stat utility on linux systems where the
  birthtime is not included in `os.stat`.

## v2.0.8 (2022-02-09)

- Bugfix `shell` for real.

## v2.0.7 (2022-02-09)

- Bugfix for `shell`.

## v2.0.6 (2022-02-09)

- Speed up moving files.
- `shell` action: Run command through the user's shell.

## v2.0.5 (2022-02-08)

- Fixed the migration message and docs URL

## v2.0.4 (2022-02-08)

- exclude_dir, system_exclude_dirs, exclude_files, system_exclude_files, filter and
  filter_dirs now accept single strings.
- Fixed a bug in the name filter

## v2.0.3 (2022-02-07)

- Fixed typo: `system_exlude_files`

## v2.0.2 (2022-02-07)

- Bugfix in env variable expansion in locations

## v2.0.1 (2022-02-07)

- Small bugfix in `macos_tags` action.
- Bugfix in the migration detection.

## v2.0.0 (2022-02-07)

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
- The [`duplicate`](docs/filters.md#duplicate) now supports several options on how to
  distinguish between original and duplicate file.
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
