# Filters

This page shows the specifics of each filter. For basic filter usage and options have a
look at the [Config](01-config.md) section.

## created

::: organize.filters.Created

**Examples**

```yaml
- : rules:
      - name: Show all files on your desktop created at least 10 days ago
        folders: "~/Desktop"
        filters:
          - created:
              days: 10
        actions:
          - echo: "Was created at least 10 days ago"
```

```yaml
rules:
  - name: Show all files on your desktop which were created within the last 5 hours
    folders: "~/Desktop"
    filters:
      - created:
          hours: 5
          mode: newer
    actions:
      - echo: "Was created within the last 5 hours"
```

```yaml
rules:
  - name: Sort pdfs by year of creation
    folders: "~/Documents"
    filters:
      - extension: pdf
      - created
    actions:
      - move: "~/Documents/PDF/{created.year}/"
```

## duplicate

::: organize.filters.Duplicate

```yaml
rules:
  - name: Show all duplicate files in your desktop and download folder (and their subfolders)
    folders:
      - ~/Desktop
      - ~/Downloads
    subfolders: true
    filters:
      - duplicate
    actions:
      - echo: "{path} is a duplicate of {duplicate}"
```

## empty

::: organize.filters.Empty

```yaml
rules:
  - name: "Recursively delete empty folders"
    targets: dirs
    locations:
      - path: ~/Desktop
        max_depth: null
    filters:
      - empty
    actions:
      - delete
```

## exif

::: organize.filters.Exif

## extension

::: organize.filters.Extension

## filecontent

::: organize.filters.FileContent

## hash

::: organize.filters.Hash

## name

::: organize.filters.Name

## size

::: organize.filters.Size

## lastmodified

::: organize.filters.LastModified

## mimetype

::: organize.filters.MimeType

## python

::: organize.filters.Python

## regex

::: organize.filters.Regex
