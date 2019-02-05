# Changelog

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
