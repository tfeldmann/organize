# Configuration

## Editing the configuration

organize has a default config file if no other file is given.

To edit the default configuration file:

```sh
organize edit  # opens in $EDITOR
organize edit --editor=vim
EDITOR=code organize edit
```

To open the folder containing the configuration file:

```sh
organize reveal
organize reveal --path  # show the full path to the default config
```

To check your configuration run:

```sh
organize check
organize check --debug  # check with debug output
```

## Running and simulating

To run / simulate the default config file:

```sh
organize sim
organize run
```

To run / simulate a specific config file:

```shell
organize sim [FILE]
organize run [FILE]
```

Optionally you can specify the working directory like this:

```shell
organize sim [FILE] --working-dir=~/Documents
```

## Environment variables

- `ORGANIZE_CONFIG` - The path to the default config file.
- `NO_COLOR` - if this is set, the output is not colored.
- `EDITOR` - The editor used to edit the config file.

## Parallelize jobs

To speed up organizing you can run multiple organize processes simultaneously like this
(linux / macOS):

```shell
organize run config_1.yaml & \
organize run config_2.yaml & \
organize run config_3.yaml &
```

Make sure that the config files are independent from each other, meaning that no rule
depends on another rule in another config file.
