# Locations

**Locations** are the folders in which organize searches for resources.
You can set multiple locations for each rule if you want.

A minimum location definition is just a path where to look for files / folders:

```yml
rules:
  - locations: ~/Desktop
    actions: ...
```

If you want to handle multiple locations in a rule, create a list:

```yaml
rules:
  - locations:
      - ~/Desktop
      - /usr/bin/
      - "%PROGRAMDATA%/test"
    actions: ...
```

Using options:

```yaml
rules:
  - name: "Location list"
    locations:
      - path: "~/Desktop"
        max_depth: 3
    actions: ...
```

Note that you can use environment variables in your locations.

## Location options

```yaml
rules:
  - locations:
      - path: ...
        max_depth: ...
        search: ...
        exclude_files: ...
        exclude_dirs: ...
        system_exlude_files: ...
        system_exclude_dirs: ...
        ignore_errors: ...
        filter: ...
        filter_dirs: ...
        filesystem: ...
```

**path** (`str`)<br>
Path to a local folder or a [Filesystem URL](#filesystems).

**max_depth** (`int` or `null`)<br>
Maximum directory depth to search.

**search** (`"breadth"` or `"depth"`)<br>
Whether to use breadth or depth search to recurse into subfolders. Note that if you
want to move or delete files from this location, this has to be set to `"depth"`.
_(Default: `"depth"`)_

**exclude_files** (`List[str]`)<br>
A list of filename patterns that should be excluded in this location, e.g. `["~*"]`.

**exclude_dirs** (`List[str]`)<br>
A list of patterns that will filter be used to filter out directory names in this location.
e.g. `['do-not-move', '*-Important']`

**system_exlude_files** (`List[str]`)<br>
The list of filename patterns that are excluded by default. Defaults to:
`["thumbs.db", "desktop.ini", "~$*", ".DS_Store", ".localized"]`

**system_exclude_dirs** (`List[str]`)<br>
The list of dir names that are excluded by default (`['.git', '.svn']`)

**ignore_errors** (`bool`)<br>
If `true`, any errors reading the location will be ignored.

**filter** (`List[str]`)<br>
A list of filename patterns that should be used in this location, e.g. `["*.py"]`.
All other files are skipped.

**filter_dirs** (`List[str]`)<br>
A list of patterns to match directory names that are included in this location.
All other directories are skipped.

**filesystem** (str)<br>
A [Filesystem URL](#filesystems).

### `filesystem` and `path`

If you want the location to be the root (`"/"`) of a filesystem, use `path`:

```yaml
rules:
  - locations:
      - path: zip:///Users/theuser/Downloads/Test.zip
```

If you want the location to be a subfolder inside a filesystem, use `path` and `filesystem`:

```yaml
rules:
  - locations:
      - filesystem: zip:///Users/theuser/Downloads/Test.zip
        path: "/folder/in/the/zipfile/"
```

### `max_depth` and `subfolders`

- If `subfolders: true` is specified on the rule, all locations are set to `max_depth: null`
  by default.
- A `max_depth` setting in a location is given precedence over the rule's `subfolders` setting.

## Remote filesystems and archives

Locations in organize can include:

- Folders on the harddrive
- ZIP archives
- TAR archives
- FTP servers
- S3 Buckets
- SSH and SMB connections
- IMAP servers
- WebDAV storages
- Dropbox / OneDrive / Google Drive storage (no need to install the client)
- Azure Datalake / Google Cloud Storage
- [and many more!](https://www.pyfilesystem.org/page/index-of-filesystems)

You can uses these just like the local harddrive, move/copy files or folders between
them or organize them however you want.

Filesystem URLs are formatted like this:

```sh
<protocol>://<username>:<password>@<resource>

# Examples:
ftp://ftp.example.org/pub
ftps://will:daffodil@ftp.example.org/private
zip://projects.zip
s3://mybucket
dropbox://dropbox.com?access_token=<dropbox access token>
ssh://[user[:password]@]host[:port]
```

The ZIP, TAR, FTP and AppFS filesystems are builtin.
For all other filesystems you need to
[install the appropriate library](https://www.pyfilesystem.org/page/index-of-filesystems).

**FTP Example**

Show the size of all JPGs on a remote FTP server and put them into a local ZIP file.

```yaml
rules:
  - locations: "ftps://demo:{env.FTP_PASSWORD}@demo.wftpserver.com"
    subfolders: true
    filters:
      - size
      - extension: jpg
    actions:
      - echo: "Found file! Size: {size.decimal}"
      - copy:
          dest: "{relative_path}"
          filesystem: zip:///Users/thomas/Desktop/ftpfiles.zip
```

**Note:**

You should never include a password in a config file. Better pass them in via an
environment variable (`{env.FTP_PASSWORD}`) as you can see above.

## Relative locations

Locations can be relative. This allows you to create simple one-off rules that can be
copied between projects.

There is a command line option to change the working directory should you need it.

```yaml
# huge-pic-warner.yaml
rules:
  - locations: "docs" # here "docs" is relative to the current working dir
    filters:
      - extension: jpg
      - size: ">3 MB"
    actions:
      - echo: "Warning - huge pic found!"
```

Then run it with:

```sh
organize sim huge-pic-warner.yaml --working-dir=some/other/dir/
```
