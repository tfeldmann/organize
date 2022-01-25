# Actions

## copy

::: organize.actions.copy.Copy

## delete

::: organize.actions.delete.Delete

```yaml
rules:
  - locations: "~/Downloads"
  - filters:
      - lastmodified:
          days: 365
      - extension:
          - png
          - jpg
  - actions:
      - delete
```

## echo

::: organize.actions.Echo

<details><summary>Examples</summary>
Prints "Found old file" for each file older than one year:

```yaml
rules:
  - locations: ~/Desktop
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

Add a single tag

```yaml
rules:
  - locations: "~/Documents/Invoices"
  - filters:
      - filename:
          startswith: "Invoice"
      - extension: pdf
  - actions:
      - macos_tags: Invoice
```

Adding multiple tags ("Invoice" and "Important")

```yaml
rules:
  - locations: "~/Documents/Invoices"
  - filters:
      - filename:
          startswith: "Invoice"
      - extension: pdf
  - actions:
      - macos_tags:
          - Important
          - Invoice
```

Specify tag colors

```yaml
rules:
  - locations: "~/Documents/Invoices"
  - filters:
      - filename:
          startswith: "Invoice"
      - extension: pdf
  - actions:
      - macos_tags:
          - Important (green)
          - Invoice (purple)
```

Add a templated tag with color

```yaml
rules:
  - locations: "~/Documents/Invoices"
  - filters:
      - created
  - actions:
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
  - locations: "~/Desktop"
  - filters:
      - lastmodified:
          years: 1
          mode: older
      - extension:
          - png
          - jpg
  - actions:
      - trash
```
