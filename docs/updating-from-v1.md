# Updating from organize v1.x

First of all, thank you for being a long time user of `organize`.

As this project is only maintained by the single person writing this article it is not
feasible to write an automatic config file migration or a compatibility layer.
Many people use organize for important documents and personal files, this is not
something I want to half-ass.

So if you want all the new goodies, you'll need to do some changes in your config.
Otherwise feel free to pin organize to the latest v1.x.

<!--
Alternative for
{created.year}-{created.month:02}-{created.day:02}

-->

## Config

- `folders` must be renamed to `locations`. New options: [Locations](locations.md).
  - the **glob syntax** (eg. `"~/Documents/**"`) has been removed.
  - the **exclamation mark exclude** (eg. `"! ~/Desktop"`) syntax has been removed.
  - They are replaced by the `max_depth`, `exclude_files`, `exclude_dirs`, `filter` and
    `filter_dirs` settings. See [Locations](locations.md).
- the `subfolders` setting is removed and replaced by the `max_depth` setting
  of a specific location.
- You can now name your rules via `name`.
- The `enabled` setting has been removed. # TODO: ?

organize v1.x:

```yml
rules:
  # find some pdf files in various dirs and echo "Hello" for each one
  - folders:
      - "~/Desktop/**/*.pdf"
      - "! ~/Desktop/donotmove/*"
    subfolders: true
    ...

  # move all pdfs into documents
  - folders:
      - "~/Downloads/*.pdf"
    ...
```

becomes (organize v2.x)

```yml
rules:
  - name: find some pdf files in various dirs and echo "Hello" for each one
    locations:
      - path: ~/Desktop/
        max_depth: null
        filter: "*.pdf"
        exclude_dirs: donotmove
    ...

  - name: move all pdfs into documents
    locations: "~/Downloads"
    filters:
      - extension: pdf
    ...
```

## Filters

- [`created`](filters.md#created) no longer accepts a timezone and uses the local timezone by default.
- [`lastmodified`](filters.md#lastmodified) no longer accepts a timezone and uses the local timezone by default.
- [`filename`](filters.md#name) is renamed to `name`.
- [`filesize`](filters.md#size) is renamed to `size`.

## Actions

- [`copy`](actions.md#copy) arguments changed.
