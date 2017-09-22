# organize
_Warning: This project is currently not yet usable. Work is in progress!_

`organize` is a file organizer for the command line. It automatically organizes your files according to your rules.

# Usage
```
organize simulate
organize run
organize config
organize --help
organize --version

Arguments:
    simulate        Simulate organizing your files. This allows you to check your rules.
    run             Applies the actions. No simulation.
    config          Open configuration in %{EDITOR}

Options:
    --version       Show program version and exit.
    -h, --help      Show this screen and exit.
```

# Example config
You can find your config.yaml file location with the command
```
organize config
```

Example `config.yaml`:
```yaml
folders: &all
  - '~/Desktop/__Inbox__'
  - '~/Download'
  - '~/TF Cloud/Office/_EINGANG_'

rules:
  # German VDI Nachrichten
  - filters:
    - PaperVdi
    actions:
    - Move: {dest: '~/Documents/VDI Nachrichten/VDI {year}-{month:02}-{day:02}.pdf'}
    folders: *all

  # Matches filename by regular expression
  - filters:
    - Regex: {expr: '^RG(\d{12})-sig\.pdf$'}
    actions:
    - Move: {dest: '~/TF Cloud/Office/Rechnungen/MCF 1und1'}
    folders: *all

  # 1und1 invoices
  - filters:
    - Invoice1and1
    actions:
    - Move: {dest: '~/TF Cloud/Office/Rechnungen/{year}-{month:02}-{day:02} 1und1.pdf'}
    folders: *all
```

## TODO
Must:
- [ ] `setup.py` file
- [ ] User config file
- [ ] Action: Copy(dest)
- [ ] Action: Rename(dest)
- [ ] Action: Shell(cmd)
- [ ] Filter: Regex with named groups
- [ ] Filter: OlderThan(date)
- [ ] Filter: NewerThan(date)
- [ ] Filter: FileExtension(ext)
- [ ] Action pipelines
- [ ] Filter pipelines
- [ ] Logfile

Nice to have:
- [ ] Action: Zip
- [ ] Action: Trash
- [ ] User plugins
- [ ] Undo

Done:
- [x] Filter: PaperVdi
- [x] Filter: Invoice1and1
- [x] Filter: Regex
- [x] Action: Move
