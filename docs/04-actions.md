# Actions

This page shows the specifics of each action. For basic action usage and options have a
look at the [Config](01-config.md) section.

## copy

::: organize.actions.copy.Copy

**Examples**

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

**Examples**

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

````yaml
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

<details><summary>Examples</summary>

```yaml
rules:
  - name: "Find files older than a year"
    locations: ~/Desktop
    filters:
      - lastmodified:
          days: 365
    actions:
      - echo: "Found old file"
````

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
      - ~/Desktop
      - ~/Downloads
    subfolders: true
    actions:
      - echo: "Basedir: {basedir}"
      - echo: "Path:    {path}"
```

</details>

## macos_tags

::: organize.actions.MacOSTags

<details>
<summary>Examples</summary>

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

</details>

## move

::: organize.actions.Move

## python

::: organize.actions.Python

## rename

::: organize.actions.Rename

## shell

::: organize.actions.Shell

## trash

::: organize.actions.Trash

Example:

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
