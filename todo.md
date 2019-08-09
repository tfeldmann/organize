# TODO

## Next up:
- [ ] Tests: Integration tests
- [ ] Config: Rule names
- [ ] CLI: Run rules by name
- [ ] Core: Clean up global config variable
- [ ] Filter: Duplicates (https://stackoverflow.com/a/36113168/300783)
- [ ] Filter: FileSize(bigger_than='2 MB', smaller_than='3 Gb')
- [ ] Filter: Content / FileContent (#10)
- [ ] Core: Normalize to unicode NFKD for all comparisons
- [ ] Docs: Why use this instead of XYZ? (UTF-8, safe by default, multiplatform quirks,
            does not spy on you)

## Maybe sometime:
- [ ] Deploy: Test with AppVeyor
- [ ] Config: Allow one yaml document per rule syntax ("---") for running rules by name
- [ ] Config: 'exclude' directive in rule (like 'filter') -> mode any, all?
- [ ] Config: Warning if multiple rules apply to the same file?
- [ ] Config: Filter modes all, none, any?
- [ ] Config: jsonschema for user config validation?
- [ ] Config: Flatten filter lists
- [ ] Config: Support ansible 'with_item' list syntax
- [ ] Core: User plugins
- [ ] Core: show docstring of individual filters, actions in help
- [ ] Core: Use Jinja2 native types instead of python format strings?
            This would allow method execution. Maybe works nicely with taggo?
- [ ] Core: Undo where possible (#16)
- [ ] Core: Add Support for S3, SSH, FTP etc. via PyFilesystem
- [ ] Action: DeleteFolderIfEmpty
- [ ] Action: Zip
- [ ] Action: E-Mail
- [ ] Action: Print (on printer)
- [ ] Action: Notify (desktop notification)
- [ ] Action: Symlink
- [ ] Filter: Python (+ docs)
- [ ] Filter: id3 tag data
- [ ] Filter: Exif data (camera__contains, ...) (https://pypi.org/project/ExifRead/)
- [ ] Filter: MD5
- [ ] Filter: Hashtags(query 'people-john,stars>4,USA') -> List / str of hashtags (#1)

## Done:
- [x] Core: Clean up global config variable  @2019-08-09
- [x] Filter: CreationDate (#13)  @2019-07-23
- [x] Config: Case insensitive filter and action matching  @2019-07-03
- [x] Format all code with `black`  @2019-07-02
- [x] Use poetry for dependencies  @2019-06-05
- [x] Config: Import config files from custom locations (#14)  @2019-06-05
- [x] Filter: Add `counter_separator` option to Move, Rename, Copy  @2018-10-05
- [x] Documentation: for `counter_separator`  @2018-10-05
- [x] Documentation: Glob folder / file exclusion  @2018-09-21
- [x] Config: '!' before globstr to exclude folders  @2018-07-09
- [x] Documentation: glob syntax  @2018-07-06
- [x] Documentation: {relative_path}  @2018-07-06
- [x] Core: add {relative_path} variable  @2018-07-06
- [x] Config: glob support (needs automatic basedir detection)  @2018-07-06
- [x] Core: Show location of files in subfolders  @2018-03-19
- [x] Filter: Extension - remove colon  @2018-03-13
- [x] Documentation: subfolders  @2018-03-13
- [x] Documentation: system_files  @2018-03-13
- [x] Config: 'subfolders' directive in rule  @2018-03-13
- [x] Proof-read docs before releasing  @2018-03-10
- [x] Documentation for {path}  @2018-03-10
- [x] Documentation for {basedir}  @2018-03-10
- [x] Quickstart with examples (Put all screenshots in folder, trash old unfinished downloads)  @2018-03-08
- [x] Core: Increment existing counters in filename  @2018-03-03
- [x] Test: Copy  @2018-03-03
- [x] Core: {basedir} needed for subfolders  @2018-03-03
- [x] Test: LastModified  @2018-03-03
- [x] Logfile  @2018-03-02
- [x] Documentation for Copy  @2018-03-01
- [x] Action: Copy(dest)  @2018-03-01
- [x] Action: Rename(dest)  @2018-02-23
- [x] Documentation for Rename  @2018-02-23
- [x] Documentation for LastModified @2018-02-14
- [x] Documentation for Filename @2018-02-14
- [x] Filter: FileName(startswith='', contains='', endswith='', case_sensitive=True) @2018-02-14
- [x] Filter: LastModified(years=0, months=0, days=0, hours=0, minutes=0, seconds=0) @2018-02-14
- [x] Allow no filters -> empty filter list @2017-11-01
- [x] Flatten Filter Extension input @2017-11-01
- [x] Action: Python inline code @2017-10-22
- [x] Regex parse result namespace @2017-10-22
- [x] Formatted output @2017-10-15
- [x] Filter pipelines @2017-10-08
- [x] Accept single folders in config @2017-10-07
- [x] Accept lists and single strings as input for filters and actions @2017-10-07
- [x] Action: Trash @2017-10-05
- [x] Filter: FileExtension(ext) @2017-10-05
- [x] Filter: Regex with named groups @2017-10-05
- [x] Flatten folder list @2017-10-05
- [x] Action: Echo @2017-09-29
- [x] Action pipelines @2017-09-28
- [x] User config file @2017-09-28
- [x] Filter and action listing @2017-09-28
- [x] `setup.py` file
- [x] Action: Shell(cmd)
- [x] Filter: Regex
- [x] Action: Move

## Dismissed:
- [ ] Filter: IncompleteDownloads (Can be done with Extension)
- [ ] Filter: FileType(type='media') (`file` utility not available on windows)
- [ ] Config: A way to exclude dotfiles (can be done with the `exclude` syntax)
- [ ] Config: A way to exclude common system files (.DS_Store, ...) (`exclude`)
- [ ] Filter: PaperVdi (too specific, can be done with Regex)
- [ ] Filter: Invoice1and1 (too specific and fragile)
