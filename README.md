<p align="center">
 <img width="623" height="168" src="https://github.com/tfeldmann/organize/raw/master/docs/images/organize.svg?sanitize=true" alt="organize logo">
</p>

<div align="center">

[![tests](https://github.com/tfeldmann/organize/actions/workflows/tests.yml/badge.svg)](https://github.com/tfeldmann/organize/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/organize/badge/?version=latest)](https://organize.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/organize-tool)](https://pypi.org/project/organize-tool/)

</div>

---

<p align="center"> <b>organize</b> - The file management automation tool
<br>
<a href="https://organize.readthedocs.io/" target="_blank">Full documentation at Read the docs</a>
</p>

- [About](#about)
- [Getting started](#getting-started)
  - [Installation](#installation)
  - [Creating your first rule](#creating-your-first-rule)
- [Example rules](#example-rules)
- [Advanced usage](#advanced-usage)
- [Command line interface](#command-line-interface)

## About

Your desktop is a mess? You cannot find anything in your downloads and
documents? Sorting and renaming all these files by hand is too tedious?
Time to automate it once and benefit from it forever.

**organize** is a command line, open-source alternative to apps like Hazel (macOS)
or File Juggler (Windows).

## Getting started

### Installation

Python 3.6+ is needed. Install it via your package manager or from [python.org](https://python.org).

Installation is done via pip. Note that the package name is `organize-tool`:

```bash
pip3 install -U organize-tool
```

If you want the text extraction possibilites, install with e xtra `textract` like this:

```bash
pip3 install -U organize-tool[textract]
```

This command can also be used to update to the newest version. Now you can run `organize --help` to check if the installation was successful.

### Creating your first rule

In your shell, **run `organize config`** to edit the configuration:

```yaml
rules:
    - folders: ~/Downloads
      subfolders: true
      filters:
          - extension: pdf
      actions:
          - echo: "Found PDF!"
```

> If you have problems editing the configuration you can run `organize config --open-folder` to reveal the configuration folder in your file manager. You can then edit the `config.yaml` in your favourite editor.
>
> Alternatively you can run `organize config --path` to see the full path to
> your `config.yaml`)

**Save your config file and run `organize run`.**

You will see a list of all `.pdf` files you have in your downloads folder (+ subfolders). For now we only show the text `Found PDF!` for each file, but this will change soon...
(If it shows `Nothing to do` you simply don't have any pdfs in your downloads folder).

Run `organize config` again and add a `copy`-action to your rule:

```yaml
actions:
    - echo: "Found PDF!"
    - move: ~/Documents/PDFs/
```

**Now run `organize sim` to see what would happen without touching your files**. You will see that your pdf-files would be moved over to your `Documents/PDFs` folder.

Congratulations, you just automated your first task. You can now run `organize run` whenever you like and all your pdfs are a bit more organized. It's that easy.

> There is so much more. You want to rename / copy files, run custom shell- or python scripts, match filenames with regular expressions or use placeholder variables? organize has you covered. Have a look at the advanced usage example below!

## Example rules

Here are some examples of simple organization and cleanup rules. Modify to your needs!

Move all invoices, orders or purchase documents into your documents folder:

```yaml
rules:
    # sort my invoices and receipts
    - folders: ~/Downloads
      subfolders: true
      filters:
          - extension: pdf
          - filename:
                contains:
                    - Invoice
                    - Order
                    - Purchase
                case_sensitive: false
      actions:
          - move: ~/Documents/Shopping/
```

Move incomplete downloads older than 30 days into the trash:

```yaml
rules:
    # move incomplete downloads older > 30 days into the trash
    - folders: ~/Downloads
      filters:
          - extension:
                - download
                - crdownload
                - part
          - lastmodified:
                days: 30
                mode: older
      actions:
          - trash
```

Delete empty files from downloads and desktop:

```yaml
rules:
    # delete empty files from downloads and desktop
    - folders:
          - ~/Downloads
          - ~/Desktop
      filters:
          - filesize: 0
      actions:
          - trash
```

Move screenshots into a "Screenshots" folder on your desktop:

```yaml
rules:
    # move screenshots into "Screenshots" folder
    - folders: ~/Desktop
      filters:
          - filename:
                startswith: "Screen Shot"
      actions:
          - move: ~/Desktop/Screenshots/
```

Organize your font downloads:

```yaml
rules:
    # organize your font files but keep the folder structure:
    #   "~/Downloads/favourites/helvetica/helvetica-bold.ttf"
    #     is moved to
    #   "~/Documents/FONTS/favourites/helvetica/helvetica-bold.ttf"
    - folders: ~/Downloads/**/*.ttf
      actions:
          - Move: "~/Documents/FONTS/{relative_path}"
```

You'll find many more examples in the <a href="https://organize.readthedocs.io/" target="_blank">full documentation</a>.

## Advanced usage

This example shows some advanced features like placeholder variables, pluggable
actions, recursion through subfolders and glob syntax:

```yaml
rules:
    - folders: ~/Documents/**/*
      filters:
          - extension:
                - pdf
                - docx
          - created
      actions:
          - move: "~/Documents/{extension.upper}/{created.year}{created.month:02}/"
          - shell: 'open "{path}"'
```

Given we have two files in our `~/Documents` folder (or any of its subfolders)
named `script.docx` from january 2018 and `demo.pdf` from december 2016 this will
happen:

-   `script.docx` will be moved to `~/Documents/DOCX/2018-01/script.docx`
-   `demo.pdf` will be moved to `~/Documents/PDF/2016-12/demo.pdf`
-   The files will be opened (`open` command in macOS) _from their new location_.
-   Note the format syntax for `{created.month}` to make sure the month is prepended with a zero.

## Command line interface

```
The file management automation tool.

Usage:
    organize sim [--config-file=<path>]
    organize run [--config-file=<path>]
    organize config [--open-folder | --path | --debug] [--config-file=<path>]
    organize list
    organize --help
    organize --version

Arguments:
    sim             Simulate a run. Does not touch your files.
    run             Organizes your files according to your rules.
    config          Open the configuration file in $EDITOR.
    list            List available filters and actions.
    --version       Show program version and exit.
    -h, --help      Show this screen and exit.

Options:
    -o, --open-folder  Open the folder containing the configuration files.
    -p, --path         Show the path to the configuration file.
    -d, --debug        Debug your configuration file.

Full documentation: https://organize.readthedocs.io
```
