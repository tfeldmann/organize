# Organize menu bar app

A small SwiftUI app that shows what `organize watch` is doing:

- whether the watcher is running, with **Pause / Resume**
- files and folders waiting in `_Review`, with **Move to** a category
- recently sorted items (click to show them in Finder)
- **Undo last run**, and shortcuts to the watched folders, the config and the log
- a notification whenever files are sorted

It does not move files itself: every action runs the Python engine of this project
(`organize move`, `organize undo`, `scripts/macos-service.sh`), so everything ends
up in the undo history.

## Build and install

Needs macOS 14 and the Xcode Command Line Tools (`xcode-select --install`).

```sh
macos/build-app.sh            # builds ~/Applications/Organize.app and opens it
macos/build-app.sh myconfig   # show another organize config than "downloads"
macos/test.sh                 # run the tests
```

The app runs the engine in this project folder. Build it again if you move the
project. "Open at login" in the app's menu starts it when you log in; the watcher
itself is started by `scripts/macos-service.sh install`.

## Debugging

Set `ORGANIZE_DEBUG_WINDOW=1` to also show the panel in a normal window, e.g. to
take a screenshot of it:

```sh
cd macos/OrganizeBar && swift build
ORGANIZE_DEBUG_WINDOW=1 ORGANIZE_PROJECT="$PWD/../.." .build/debug/OrganizeBar
```
