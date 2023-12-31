<p align="center">
  <img width="623" height="168" src="https://github.com/tfeldmann/organize/raw/gh-pages/img/organize.svg?sanitize=true" alt="organize logo">
</p>

<div align="center">

<a href="https://github.com/tfeldmann/organize/actions/workflows/tests.yml">
  <img src="https://github.com/tfeldmann/organize/actions/workflows/tests.yml/badge.svg" title="tests">
</a>
<a href="https://organize.readthedocs.io/en/latest/?badge=latest">
  <img src="https://readthedocs.org/projects/organize/badge/?version=latest" title="Documentation Status">
</a>
<a href="https://github.com/tfeldmann/organize/blob/main/LICENSE.txt">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" title="License">
</a>
<a href="https://pypi.org/project/organize-tool/">
  <img src="https://img.shields.io/pypi/v/organize-tool" title="PyPI Version">
</a>

</div>

---

<p align="center"> <b>organize</b> - The file management automation tool
<br>
<a href="https://organize.readthedocs.io/" target="_blank">Full documentation at Read the docs</a>
</p>


## Testers needed! Help testing the v3-alpha

A prerelease of organize v3 is available. To install:

```sh
# Installs the pre release!
pip install -U organize-tool --pre

# Installs the pre release with text extraction utils.
pip install -U organize-tool[textract] --pre
```

The new version should be *much* faster and fixes a lot of bugs. It also comes with
a some new actions, filters and options.

- [See the changelog](https://tfeldmann.github.io/organize/changelog/)
- [Migration guide](https://tfeldmann.github.io/organize/migrating/#migrating-from-v2-to-v3).

## About

Your desktop is a mess? You cannot find anything in your downloads and
documents? Sorting and renaming all these files by hand is too tedious?
Time to automate it once and benefit from it forever.

**organize** is a command line, open-source alternative to apps like Hazel (macOS)
or File Juggler (Windows).

## Features

Some highlights include:

- Safe moving, renaming, copying of files and folders with conflict resolution options.
- Fast duplicate file detection.
- Exif tags extraction.
- Categorization via text extracted from PDF, DOCX and many more.
- Powerful template engine.
- Inline python and shell commands as filters and actions for maximum flexibility.
- Everything can be simulated before touching your files.
- Works on macOS, Windows and Linux.
- Free and open source software.

## Getting started

### Installation

Only python 3.8+ is needed.
Install it via your package manager or from [python.org](https://python.org).

Installation is done via pip. Note that the package name is `organize-tool`:

```bash
pip install -U organize-tool
```

If you want the text extraction capabilities, install with `textract` like this (the
qoutes are important):

```bash
pip install "organize-tool[texttract]"
```

This command can also be used to update to the newest version. Now you can run `organize --help` to check if the installation was successful.

### Create your first rule

In your shell, run `organize new` and then `organize edit` to edit the configuration:

```yaml
rules:
  - name: "Find PDFs"
    locations:
      - ~/Downloads
    subfolders: true
    filters:
      - extension: pdf
    actions:
      - echo: "Found PDF!"
```

> If you have problems editing the configuration you can run `organize show --reveal` to reveal the configuration folder in your file manager. You can then edit the `config.yaml` in your favourite editor.

save your config file and run:

```sh
organize run
```

You will see a list of all `.pdf` files you have in your downloads folder (+ subfolders).
For now we only show the text `Found PDF!` for each file, but this will change soon...
(If it shows `Nothing to do` you simply don't have any pdfs in your downloads folder).

Run `organize edit` again and add a `move`-action to your rule:

```yml
actions:
  - echo: "Found PDF!"
  - move: ~/Documents/PDFs/
```

Now run `organize sim` to see what would happen without touching your files.

You will see that your pdf-files would be moved over to your `Documents/PDFs` folder.

Congratulations, you just automated your first task. You can now run `organize run`
whenever you like and all your pdfs are a bit more organized. It's that easy.

> There is so much more. You want to rename / copy files, run custom shell- or python scripts, match names with regular expressions or use placeholder variables? organize has you covered. Have a look at the advanced usage example below!

## Example rules

Here are some examples of simple organization and cleanup rules. Modify to your needs!

Move all invoices, orders or purchase documents into your documents folder:

```yaml
rules:
  - name: "Sort my invoices and receipts"
    locations: ~/Downloads
    subfolders: true
    filters:
      - extension: pdf
      - name:
          contains:
            - Invoice
            - Order
            - Purchase
          case_sensitive: false
    actions:
      - move: ~/Documents/Shopping/
```

Recursively delete all empty directories:

```yaml
rules:
  - name: "Recursively delete all empty directories"
    locations:
      - path: ~/Downloads
    targets: dirs
    subfolders: true
    targets: dirs
    filters:
      - empty
    actions:
      - delete
```

<!--<details markdown="1">
  <summary markdown="1">Advanced example</summary>

This example shows some advanced features like placeholder variables, pluggable
actions, limited recursion through subfolders and filesystems (FTP and ZIP):

This rule:

- Searches recursively in your documents folder (three levels deep) and on a FTP server
- for files with **pdf** or **docx** extension
- that have a created timestamp
- Asks for user confirmation for each file
- Moves them according to their extensions and **created** timestamps:
- `script.docx` will be moved to `~/Documents/DOCX/2018-01/script.docx`
- `demo.pdf` will be moved to `~/Documents/PDF/2016-12/demo.pdf`
- If this new is already taken, a counter is appended to the filename ("rename_new")
- Creates a zip backup file on your desktop containing all files.

```yaml
rules:
  - name: "Download, cleanup and backup"
    locations:
      - path: ~/Documents
        max_depth: 3
      - path: ftps://demo:demo@demo.wftpserver.com
    filters:
      - extension:
          - pdf
          - docx
      - created
    actions:
      - confirm:
          msg: "Really continue?"
          default: true
      - move:
          dest: "~/Documents/{extension.upper()}/{created.strftime('%Y-%m')}/"
          on_conflict: rename_new
      - copy: "zip:///Users/thomas/Desktop/backup.zip"
```

</details>-->

You'll find many more examples in the <a href="https://tfeldmann.github.io/organize" target="_blank">full documentation</a>.

## Command line interface

```txt
organize - The file management automation tool.

Usage:
  organize run   [options] [<config>]
  organize sim   [options] [<config>]
  organize new   [<config>]
  organize edit  [<config>]
  organize check [<config>]
  organize debug [<config>]
  organize show  [--path|--reveal] [<config>]
  organize list
  organize docs
  organize --version
  organize --help

Commands:
  run        Organize your files.
  sim        Simulate organizing your files.
  new        Creates a new config.
  edit       Edit the config file with $EDITOR.
  check      Check whether the config file is valid.
  debug      Shows the raw config parsing steps.
  show       Print the config to stdout.
               Use --reveal to reveal the file in your file manager
               Use --path to show the path to the file
  list       Lists config files found in the default locations.
  docs       Open the documentation.

Options:
  <config>                        A config name or path to a config file
  -W --working-dir <dir>          The working directory
  -F --format (default|jsonl)     The output format [Default: default]
  -T --tags <tags>                Tags to run (eg. "initial,release")
  -S --skip-tags <tags>           Tags to skip
  -h --help                       Show this help page.
```

## Other donation options:

ETH:

```
0x8924a060CD533699E230C5694EC95b26BC4168E7
```

BTC:

```
39vpniiZk8qqGB2xEqcDjtWxngFCCdWGjY
```
