# Configuration

## Editing the configuration

organize has a default config file if no other file is given.

To edit the default configuration file:

```sh
$ organize edit  # opens in $EDITOR
$ organize edit --editor=vim
$ EDITOR=code organize edit
```

To open the folder containing the configuration file:

```sh
$ organize reveal
$ organize reveal --path  # show the full path to the default config
```

To check your configuration run:

```sh
$ organize check
$ organize check --debug  # check with debug output
```

## Running and simulating

To run / simulate the default config file:

```sh
$ organize sim
$ organize run
```

To run / simulate a specific config file:

```sh
$ organize sim [FILE]
$ organize run [FILE]
```

## Environment variables

- `ORGANIZE_CONFIG` - The path to the default config file.
- `NO_COLOR` - if this is set, the output is not colored.
- `EDITOR` - The editor used to edit the config file.

## Command line interface

::: mkdocs-click
    :module: organize.cli
    :command: organize
