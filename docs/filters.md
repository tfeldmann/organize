# Filters

This page shows the specifics of each filter.

## - How to exclude filters -

To exclude a filter, prefix the filter name with **not** (e.g. `"not empty"`,
`"not extension": jpg`, etc).

!!! note

    If you want to exclude all filters you can set the rule's `filter_mode` to `none`.

Example:

```yaml
rules:
  # using filter_mode
  - locations: ~/Desktop
    filter_mode: "none" # <- excludes all
    filters:
      - empty
      - name:
          endswith: "2022"
    actions:
      - echo: "{name}"

  # Exclude a single filter
  - locations: ~/Desktop
    filters:
      - not extension: jpg # <- matches all non-jpgs
      - name:
          startswith: "Invoice"
      - not empty # <- matches files with content
    actions:
      - echo: "{name}"
```

## created

::: organize.filters.Created

**Examples:**

Show all files on your desktop created at least 10 days ago

```yaml
rules:
  - name: Show all files on your desktop created at least 10 days ago
    locations: "~/Desktop"
    filters:
      - created:
          days: 10
    actions:
      - echo: "Was created at least 10 days ago"
```

Show all files on your desktop which were created within the last 5 hours

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

Sort pdfs by year of creation

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

Formatting the creation date

```yaml
rules:
  - name: Display the creation date
    locations: "~/Documents"
    filters:
      - extension: pdf
      - created
    actions:
      - echo: "ISO Format:   {created.strftime('%Y-%m-%d')}"
      - echo: "As timestamp: {created.timestamp() | int}"
```

## date_added

::: organize.filters.DateAdded

Works the same way as [`created`](#created) and [`lastmodified`](#lastmodified).

**Examples:**

```yaml
rules:
  - name: Show the date the file was added to the folder
    locations: "~/Desktop"
    filters:
      - date_added
    actions:
      - echo: "Date added: {date_added.strftime('%Y-%m-%d')}"
```

## date_lastused

::: organize.filters.DateLastUsed

Works the same way as [`created`](#created) and [`lastmodified`](#lastmodified).

**Examples:**

```yaml
rules:
  - name: Show the date the file was added to the folder
    locations: "~/Desktop"
    filters:
      - date_lastused
    actions:
      - echo: "Date last used: {date_lastused.strftime('%Y-%m-%d')}"
```

## duplicate

::: organize.filters.Duplicate

**Examples:**

Show all duplicate files in your desktop and download folder (and their subfolders)

```yaml
rules:
  - name: Show all duplicate files in your desktop and download folder (and their subfolders)
    locations:
      - ~/Desktop
      - ~/Downloads
    subfolders: true
    filters:
      - duplicate
    actions:
      - echo: "{path} is a duplicate of {duplicate.original}"
```

Check for duplicated files between Desktop and a Zip file, select original by creation date

```yaml
rules:
  - name: "Check for duplicated files between Desktop and a Zip file, select original by creation date"
    locations:
      - ~/Desktop
      - zip://~/Desktop/backup.zip
    filters:
      - duplicate:
          detect_original_by: "created"
    actions:
      - echo: "Duplicate found!"
```

## empty

::: organize.filters.Empty

**Examples:**

Recursively delete empty folders

```yaml
rules:
  - targets: dirs
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

Show available EXIF data of your pictures

```yaml
rules:
  - name: "Show available EXIF data of your pictures"
    locations:
      - path: ~/Pictures
        max_depth: null
    filters:
      - exif
    actions:
      - echo: "{exif}"
```

Copy all images which contain GPS information while keeping subfolder structure:

```yaml
rules:
  - name: "GPS demo"
    locations:
      - path: ~/Pictures
        max_depth: null
    filters:
      - exif: gps.gpsdate
    actions:
      - copy: ~/Pictures/with_gps/{relative_path}/
```

Filter by camera manufacturer

```yaml
rules:
  - name: "Filter by camera manufacturer"
    locations:
      - path: ~/Pictures
        max_depth: null
    filters:
      - exif:
          image.model: Nikon D3200
    actions:
      - move: "~/Pictures/My old Nikon/"
```

Sort images by camera manufacturer. This will create folders for each camera model
(for example "Nikon D3200", "iPhone 6s", "iPhone 5s", "DMC-GX80") and move the pictures
accordingly:

```yaml
rules:
  - name: "camera sort"
    locations:
      - path: ~/Pictures
        max_depth: null
    filters:
      - extension: jpg
      - exif: image.model
    actions:
      - move: "~/Pictures/{exif.image.model}/"
```

## extension

::: organize.filters.Extension

**Examples:**

Match a single file extension

```yaml
rules:
  - name: "Match a single file extension"
    locations: "~/Desktop"
    filters:
      - extension: png
    actions:
      - echo: "Found PNG file: {path}"
```

Match multiple file extensions

```yaml
rules:
  - name: "Match multiple file extensions"
    locations: "~/Desktop"
    filters:
      - extension:
          - .jpg
          - jpeg
    actions:
      - echo: "Found JPG file: {path}"
```

Make all file extensions lowercase

```yaml
rules:
  - name: "Make all file extensions lowercase"
    locations: "~/Desktop"
    filters:
      - extension
    actions:
      - rename: "{path.stem}.{extension.lower()}"
```

Using extension lists ([yaml aliases](rules.md#advanced-aliases)

```yaml
img_ext: &img
  - png
  - jpg
  - tiff

audio_ext: &audio
  - mp3
  - wav
  - ogg

rules:
  - name: "Using extension lists"
    locations: "~/Desktop"
    filters:
      - extension:
          - *img
          - *audio
    actions:
      - echo: "Found media file: {path}"
```

## filecontent

::: organize.filters.FileContent

**Examples:**

Show the content of all your PDF files

```yaml
rules:
  - name: "Show the content of all your PDF files"
    locations: ~/Documents
    filters:
      - extension: pdf
      - filecontent
    actions:
      - echo: "{filecontent}"
```

Match an invoice with a regular expression and sort by customer

```yaml
rules:
  - name: "Match an invoice with a regular expression and sort by customer"
    locations: "~/Desktop"
    filters:
      - filecontent: 'Invoice.*Customer (?P<customer>\w+)'
    actions:
      - move: "~/Documents/Invoices/{filecontent.customer}/"
```

Exampe to filter the filename with respect to a valid date code.

The filename should start with `<year>-<month>-<day>`.

Regex:

1. creates a placeholder variable containing the year
2. allows only years which start with 20 and are followed by 2 numbers
3. months can only have as first digit 0 or 1 and must be followed by a number
4. days can only have 0, 1,2 or 3 and must followed by number
   Note: Filter is not perfect but still.

```yaml
rules:
  - locations: ~/Desktop
    filters:
      - regex: '(?P<year>20\d{2})-[01]\d-[0123]\d.*'
    actions:
      - echo: "Year: {regex.year}"
```

!!! note

    If you have trouble getting the filecontent filter to work, have a look at the
    [installation hints](textract-hints.md)

## hash

::: organize.filters.Hash

**Examples:**

Show the hashes of your files:

```yaml
rules:
  - name: "Show the hashes and size of your files"
    locations: "~/Desktop"
    filters:
      - hash
      - size
    actions:
      - echo: "{hash} {size.decimal}"
```

## lastmodified

::: organize.filters.LastModified

**Examples:**

```yaml
rules:
  - name: "Show all files on your desktop last modified at least 10 days ago"
    locations: "~/Desktop"
    filters:
      - lastmodified:
          days: 10
    actions:
      - echo: "Was modified at least 10 days ago"
```

Show all files on your desktop which were modified within the last 5 hours:

```yaml
rules:
  - locations: "~/Desktop"
    filters:
      - lastmodified:
          hours: 5
          mode: newer
    actions:
      - echo: "Was modified within the last 5 hours"
```

Sort pdfs by year of last modification

```yaml
rules:
  - name: "Sort pdfs by year of last modification"
    locations: "~/Documents"
    filters:
      - extension: pdf
      - lastmodified
    actions:
      - move: "~/Documents/PDF/{lastmodified.year}/"
```

Formatting the last modified date

```yaml
rules:
  - name: Formatting the lastmodified date
    locations: "~/Documents"
    filters:
      - extension: pdf
      - lastmodified
    actions:
      - echo: "ISO Format:   {lastmodified.strftime('%Y-%m-%d')}"
      - echo: "As timestamp: {lastmodified.timestamp() | int}"
```

## macos_tags

::: organize.filters.MacOSTags

**Examples:**

```yaml
rules:
  - name: "Only files with a red macOS tag"
    locations: "~/Downloads"
    filters:
      - macos_tags: "* (red)"
    actions:
      - echo: "File with red tag"
```

```yaml
rules:
  - name: "All files tagged 'Invoice' (any color)"
    locations: "~/Downloads"
    filters:
      - macos_tags: "Invoice (*)"
    actions:
      - echo: "Invoice found"
```

```yaml
rules:
  - name: "All files with a tag 'Invoice' (any color) or with a green tag"
    locations: "~/Downloads"
    filters:
      - macos_tags:
          - "Invoice (*)"
          - "* (green)"
    actions:
      - echo: "Match found!"
```

```yaml
rules:
  - name: "Listing file tags"
    locations: "~/Downloads"
    filters:
      - macos_tags
    actions:
      - echo: "{macos_tags}"
```

## mimetype

::: organize.filters.MimeType

**Examples:**

Show MIME types

```yaml
rules:
  - name: "Show MIME types"
    locations: "~/Downloads"
    filters:
      - mimetype
    actions:
      - echo: "{mimetype}"
```

Filter by 'image' mimetype

```yaml
rules:
  - name: "Filter by 'image' mimetype"
    locations: "~/Downloads"
    filters:
      - mimetype: image
    actions:
      - echo: "This file is an image: {mimetype}"
```

Filter by specific MIME type

```yaml
rules:
  - name: Filter by specific MIME type
    locations: "~/Desktop"
    filters:
      - mimetype: application/pdf
    actions:
      - echo: "Found a PDF file"
```

Filter by multiple specific MIME types

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

## name

::: organize.filters.Name

**Examples:**

Match all files starting with 'Invoice':

```yaml
rules:
  - locations: "~/Desktop"
    filters:
      - name:
          startswith: Invoice
    actions:
      - echo: "This is an invoice"
```

Match all files starting with 'A' end containing the string 'hole'
(case insensitive):

```yaml
rules:
  - locations: "~/Desktop"
    filters:
      - name:
          startswith: A
          contains: hole
          case_sensitive: false
    actions:
      - echo: "Found a match."
```

Match all files starting with 'A' or 'B' containing '5' or '6' and ending with
'\_end':

```yaml
rules:
  - locations: "~/Desktop"
    filters:
      - name:
          startswith:
            - "A"
            - "B"
          contains:
            - "5"
            - "6"
          endswith: _end
          case_sensitive: false
    actions:
      - echo: "Found a match."
```

## python

::: organize.filters.Python

**Examples:**

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

**Examples:**

Match an invoice with a regular expression:

```yaml
rules:
  - locations: "~/Desktop"
    filters:
      - regex: '^RG(\d{12})-sig\.pdf$'
    actions:
      - move: "~/Documents/Invoices/1und1/"
```

Match and extract data from filenames with regex named groups:
This is just like the previous example but we rename the invoice using
the invoice number extracted via the regular expression and the named
group `the_number`.

```yaml
rules:
  - locations: ~/Desktop
    filters:
      - regex: '^RG(?P<the_number>\d{12})-sig\.pdf$'
    actions:
      - move: ~/Documents/Invoices/1und1/{regex.the_number}.pdf
```

## size

::: organize.filters.Size

**Examples:**

Trash big downloads:

```yaml
rules:
  - locations: "~/Downloads"
    targets: files
    filters:
      - size: "> 0.5 GB"
    actions:
      - trash
```

Move all JPEGS bigger > 1MB and <10 MB. Search all subfolders and keep the
original relative path.

```yaml
rules:
  - locations:
      - path: "~/Pictures"
        max_depth: null
    filters:
      - extension:
          - jpg
          - jpeg
      - size: ">1mb, <10mb"
    actions:
      - move: "~/Pictures/sorted/{relative_path}/"
```
