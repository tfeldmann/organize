# Actions

This page shows the specifics of each action. For basic action usage and options have a
look at the [Config](01-config.md) section.

## confirm

::: organize.actions.Confirm

**Examples**

Confirm before deleting a duplicate

```yaml
rules:
  - name: "Delete duplicates"
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
          dest: "~/Desktop/{extension.upper}/"
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
:caption: config.yaml

rules:
  - locations:
      - ~/Desktop
    actions:
      - echo: "Hello World! {path}"
```

This will print something like `Found a PNG: "test.png"` for each file on your desktop

```yaml
:caption: config.yaml

rules:
  - locations:
      - ~/Desktop
    filters:
      - Extension
    actions:
      - echo: 'Found a {extension.upper}: "{path.name}"'
```

Show the `{basedir}` and `{path}` of all files in '~/Downloads', '~/Desktop' and their subfolders:

```yaml
:caption: config.yaml

rules:
  - locations:
      - path: ~/Desktop
        max_depth: null
      - path: ~/Downloads
        max_depth: null
    actions:
      - echo: "Basedir: {basedir}"
      - echo: "Path:    {path}"
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
          dest: "~/Desktop/{extension.upper}/"
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
          print('Name: %s' % regex.name)
          print('Extension: %s' % regex.extension)
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
          webbrowser.open('https://www.google.com/search?q=%s' % path.stem)
```

## rename

::: organize.actions.Rename

**Examples:**

```yaml
rules:
  - name: "Convert all .PDF file extensions to lowercase (.pdf)"
    locations: "~/Desktop"
    filters:
      - extension: PDF
    actions:
      - rename: "{path.stem}.pdf"
```

```yaml
rules:
  - name: "Convert **all** file extensions to lowercase"
    locations: "~/Desktop"
    filters:
      - extension
    actions:
      - rename: "{path.stem}.{extension.lower}"
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
