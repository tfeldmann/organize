# Actions

This page shows the specifics of each action. For basic action usage and options have a
look at the [Rules](rules.md) section.

## confirm

::: organize.actions.Confirm

**Examples**

Confirm before deleting a duplicate

```yaml
rules:
  - name: "Delete duplicates with confirmation"
    locations:
      - ~/Downloads
      - ~/Documents
    filters:
      - not empty
      - duplicate
      - name
    actions:
      - confirm: "Delete {name}?"
      - trash
```

## copy

::: organize.actions.Copy

**Examples:**

Copy all pdfs into `~/Desktop/somefolder/` and keep filenames

```yaml
rules:
  - locations: ~/Desktop
    filters:
      - extension: pdf
    actions:
      - copy: "~/Desktop/somefolder/"
```

Use a placeholder to copy all .pdf files into a "PDF" folder and all .jpg files into a "JPG" folder. Existing files will be overwritten.

```yaml
rules:
  - locations: ~/Desktop
    filters:
      - extension:
          - pdf
          - jpg
    actions:
      - copy:
          dest: "~/Desktop/{extension.upper()}/"
          on_conflict: overwrite
```

Copy into the folder `Invoices`. Keep the filename but do not overwrite existing files.
To prevent overwriting files, an index is added to the filename, so `somefile.jpg` becomes `somefile 2.jpg`.
The counter separator is `' '` by default, but can be changed using the `counter_separator` property.

```yaml
rules:
  - locations: ~/Desktop/Invoices
    filters:
      - extension:
          - pdf
    actions:
      - copy:
          dest: "~/Documents/Invoices/"
          on_conflict: "rename_new"
          rename_template: "{name} {counter}{extension}"
```

## delete

::: organize.actions.delete.Delete

**Examples:**

Delete old downloads.

```yaml
rules:
  - locations: "~/Downloads"
    filters:
      - lastmodified:
          days: 365
      - extension:
          - png
          - jpg
    actions:
      - delete
```

Delete all empty subfolders

```yaml
rules:
  - name: Delete all empty subfolders
    locations:
      - path: "~/Downloads"
        max_depth: null
    targets: dirs
    filters:
      - empty
    actions:
      - delete
```

## echo

::: organize.actions.Echo

**Examples:**

```yaml
rules:
  - name: "Find files older than a year"
    locations: ~/Desktop
    filters:
      - lastmodified:
          days: 365
    actions:
      - echo: "Found old file"
```

Prints "Hello World!" and filepath for each file on the desktop:

```yaml
rules:
  - locations:
      - ~/Desktop
    actions:
      - echo: "Hello World! {path}"
```

This will print something like `Found a ZIP: "backup"` for each file on your desktop

```yaml
rules:
  - locations:
      - ~/Desktop
    filters:
      - extension
      - name
    actions:
      - echo: 'Found a {extension.upper()}: "{name}"'
```

Show the `{relative_path}` and `{path}` of all files in '~/Downloads', '~/Desktop' and their subfolders:

```yaml
rules:
  - locations:
      - path: ~/Desktop
        max_depth: null
      - path: ~/Downloads
        max_depth: null
    actions:
      - echo: "Path:     {path}"
      - echo: "Relative: {relative_path}"
```

## macos_tags

::: organize.actions.MacOSTags

**Examples:**

```yaml
rules:
  - name: "add a single tag"
    locations: "~/Documents/Invoices"
    filters:
      - name:
          startswith: "Invoice"
      - extension: pdf
    actions:
      - macos_tags: Invoice
```

Adding multiple tags ("Invoice" and "Important")

```yaml
rules:
  - locations: "~/Documents/Invoices"
    filters:
      - name:
          startswith: "Invoice"
      - extension: pdf
    actions:
      - macos_tags:
          - Important
          - Invoice
```

Specify tag colors

```yaml
rules:
  - locations: "~/Documents/Invoices"
    filters:
      - name:
          startswith: "Invoice"
      - extension: pdf
    actions:
      - macos_tags:
          - Important (green)
          - Invoice (purple)
```

Add a templated tag with color

```yaml
rules:
  - locations: "~/Documents/Invoices"
    filters:
      - created
    actions:
      - macos_tags:
          - Year-{created.year} (red)
```

## move

::: organize.actions.Move

**Examples:**

Move all pdfs and jpgs from the desktop into the folder "~/Desktop/media/". Filenames are not changed.

```yaml
rules:
  - locations: ~/Desktop
    filters:
      - extension:
          - pdf
          - jpg
    actions:
      - move: "~/Desktop/media/"
```

Use a placeholder to move all .pdf files into a "PDF" folder and all .jpg files into a
"JPG" folder. Existing files will be overwritten.

```yaml
rules:
  - locations: ~/Desktop
    filters:
      - extension:
          - pdf
          - jpg
    actions:
      - move:
          dest: "~/Desktop/{extension.upper()}/"
          on_conflict: "overwrite"
```

Move pdfs into the folder `Invoices`. Keep the filename but do not overwrite existing files. To prevent overwriting files, an index is added to the filename, so `somefile.jpg` becomes `somefile 2.jpg`.

```yaml
rules:
  - locations: ~/Desktop/Invoices
    filters:
      - extension:
          - pdf
    actions:
      - move:
          dest: "~/Documents/Invoices/"
          on_conflict: "rename_new"
          rename_template: "{name} {counter}{extension}"
```

## python

::: organize.actions.Python

**Examples:**

A basic example that shows how to get the current file path and do some printing in a
for loop. The `|` is yaml syntax for defining a string literal spanning multiple lines.

```yaml
rules:
  - locations: "~/Desktop"
    actions:
      - python: |
          print('The path of the current file is %s' % path)
          for _ in range(5):
              print('Heyho, its me from the loop')
```

```yaml
rules:
  - name: "You can access filter data"
    locations: ~/Desktop
    filters:
      - regex: '^(?P<name>.*)\.(?P<extension>.*)$'
    actions:
      - python: |
          print('Name: %s' % regex["name"])
          print('Extension: %s' % regex["extension"])
```

Running in simulation and [yaml aliases](rules.md#advanced-aliases):

```yaml
my_python_script: &script |
  print("Hello World!")
  print(path)

rules:
  - name: "Run in simulation and yaml alias"
    locations:
      - ~/Desktop/
    actions:
      - python:
          code: *script
          run_in_simulation: yes
```

You have access to all the python magic -- do a google search for each
filename starting with an underscore:

```yaml
rules:
  - locations: ~/Desktop
    filters:
      - name:
          startswith: "_"
    actions:
      - python: |
          import webbrowser
          webbrowser.open('https://www.google.com/search?q=%s' % name)
```

## rename

::: organize.actions.Rename

**Examples:**

```yaml
rules:
  - name: "Convert all .PDF file extensions to lowercase (.pdf)"
    locations: "~/Desktop"
    filters:
      - name
      - extension: PDF
    actions:
      - rename: "{name}.pdf"
```

```yaml
rules:
  - name: "Convert **all** file extensions to lowercase"
    locations: "~/Desktop"
    filters:
      - name
      - extension
    actions:
      - rename: "{name}.{extension.lower()}"
```

## shell

::: organize.actions.Shell

**Examples:**

```yaml
rules:
  - name: "On macOS: Open all pdfs on your desktop"
    locations: "~/Desktop"
    filters:
      - extension: pdf
    actions:
      - shell: 'open "{path}"'
```

## symlink

::: organize.actions.Symlink

## trash

::: organize.actions.Trash

**Examples:**

```yaml
rules:
  - name: Move all JPGs and PNGs on the desktop which are older than one year into the trash
    locations: "~/Desktop"
    filters:
      - lastmodified:
          years: 1
          mode: older
      - extension:
          - png
          - jpg
    actions:
      - trash
```

## write_text

::: organize.actions.WriteText

**Examples**

```yaml
rules:
  - name: "Record file sizes"
    locations: ~/Downloads
    filters:
      - size
    actions:
      - write_text:
          text: "{size.traditional} -- {relative_path}"
          textfile: "./sizes.txt"
          mode: "append"
          clear_before_first_write: true
```

This will create a file `sizes.txt` in the current working folder which contains the
filesizes of everything in the `~/Downloads` folder:

```
2.9 MB -- SIM7600.pdf
1.0 MB -- Bildschirmfoto 2022-07-05 um 10.43.16.png
5.9 MB -- Albumcover.png
51.2 KB -- Urlaubsantrag 2022-04-19.pdf
1.8 MB -- ETH_USB_HUB_HAT.pdf
2.1 MB -- ArduinoDUE_V02g_sch.pdf
...
```

You can use templates both in the text as well as in the textfile parameter:

```yaml
rules:
  - name: "File sizes by extension"
    locations: ~/Downloads
    filters:
      - size
      - extension
    actions:
      - write_text:
          text: "{size.traditional} -- {relative_path}"
          textfile: "./sizes.{extension}.txt"
          mode: "prepend"
          clear_before_first_write: true
```

This will separate the filesizes by extension.
