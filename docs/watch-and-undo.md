# Watching and undo

## Organize new files automatically

`organize watch` runs your config whenever files are added to one of its locations:

```sh
organize watch downloads
```

It sorts the files that are already there, then waits for changes. After a new file
arrives it waits until no further changes happened for a few seconds (5 by default),
so files that are still being downloaded are not touched:

```sh
organize watch downloads --delay 10
```

Only the top level of each location is watched. The config file is read again before
every run, so changes take effect without restarting the watcher.

## Undo

Every `organize run` (and every run started by `organize watch`) is recorded.
`organize undo` moves the files of the last run back to where they were and removes
the folders it created, if they are empty:

```sh
organize undo --dry-run   # show what would be undone
organize undo             # undo the last run
organize undo             # ... and the one before
```

`organize history` lists the recorded runs. To undo a specific run, pass its id:

```sh
organize undo --run 20261031-221500-a1b2c3
```

Undo reverts `move`, `rename` and `copy` (copies are moved to the trash). Files that
were changed or moved again since the run are skipped. Actions that delete or
overwrite files (`delete`, `trash`, `on_conflict: overwrite`) cannot be undone.

## Run in the background on macOS

`scripts/macos-service.sh` installs a LaunchAgent that starts `organize watch` at
login and restarts it if it crashes:

```sh
scripts/macos-service.sh install downloads   # install and start
scripts/macos-service.sh status              # is it running?
scripts/macos-service.sh logs                # follow ~/Library/Logs/organize/watch.log
scripts/macos-service.sh uninstall           # stop and remove
```

API keys are read from the `.env` file in the project folder. macOS may ask once
whether Python is allowed to access your Downloads folder.
