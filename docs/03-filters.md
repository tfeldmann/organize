# Filters

This page shows the specifics of each filter. For basic filter usage and options have a
look at the [Config](01-config.md) section.

## created

::: organize.filters.Created

## duplicate

::: organize.filters.Duplicate

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
