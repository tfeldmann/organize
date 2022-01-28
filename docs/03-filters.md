# Filters

This page shows the specifics of each filter. For basic filter usage and options have a
look at the [Config](01-config.md) section.

## created

::: organize.filters.Created

**Examples**

```yaml
- : rules:
      - name: Show all files on your desktop created at least 10 days ago
        locations: "~/Desktop"
        filters:
          - created:
              days: 10
        actions:
          - echo: "Was created at least 10 days ago"
```

```yaml
rules:
  - name: Show all files on your desktop which were created within the last 5 hours
    locations: "~/Desktop"
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
    locations: "~/Documents"
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
    locations:
      - ~/Desktop
      - ~/Downloads
    sublocations: true
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

**Examples**

```yaml
rules:
  - name: "Show MIME types"
    locations: "~/Downloads"
    filters:
      - mimetype
    actions:
      - echo: "{mimetype}"
```

```yaml
rules:
  - name: "Filter by 'image' mimetype"
    locations: "~/Downloads"
    filters:
      - mimetype: image
    actions:
      - echo: "This file is an image: {mimetype}"
```

```yaml
rules:
  - name: Filter by specific MIME type
    locations: "~/Desktop"
    filters:
      - mimetype: application/pdf
    actions:
      - echo: "Found a PDF file"
```

```yaml
rules:
  - name: Filter by multiple specific MIME types
    locations: "~/Music"
    filters:
      - mimetype:
          - application/pdf
          - audio/midi
    actions:
      - echo: "Found Midi or PDF."
```

## python

::: organize.filters.Python

**Examples**

```yaml
rules:
  - name: A file name reverser.
    locations: ~/Documents
    filters:
      - extension
      - python: |
          return {"reversed_name": path.stem[::-1]}
    actions:
      - rename: "{python.reversed_name}.{extension}"
```

A filter for odd student numbers. Assuming the folder `~/Students` contains
the files `student-01.jpg`, `student-01.txt`, `student-02.txt` and
`student-03.txt` this rule will print
`"Odd student numbers: student-01.txt"` and
`"Odd student numbers: student-03.txt"`

```yaml
rules:
  - name: "Filter odd student numbers"
    locations: ~/Students/
    filters:
      - python: |
        return int(path.stem.split('-')[1]) % 2 == 1
      actions:
      - echo: "Odd student numbers: {path.name}"
```

Advanced usecase. You can access data from previous filters in your python code.
This can be used to match files and capturing names with a regular expression
and then renaming the files with the output of your python script.

```yaml
rules:
  - name: "Access placeholders in python filter"
    locations: files
    filters:
      - extension: txt
      - regex: (?P<firstname>\w+)-(?P<lastname>\w+)\..*
      - python: |
          emails = {
              "Betts": "dbetts@mail.de",
              "Cornish": "acornish@google.com",
              "Bean": "dbean@aol.com",
              "Frey": "l-frey@frey.org",
          }
          if regex.lastname in emails: # get emails from wherever
              return {"mail": emails[regex.lastname]}
    actions:
      - rename: "{python.mail}.txt"
```

Result:

- `Devonte-Betts.txt` becomes `dbetts@mail.de.txt`
- `Alaina-Cornish.txt` becomes `acornish@google.com.txt`
- `Dimitri-Bean.txt` becomes `dbean@aol.com.txt`
- `Lowri-Frey.txt` becomes `l-frey@frey.org.txt`
- `Someunknown-User.txt` remains unchanged because the email is not found

## regex

::: organize.filters.Regex
