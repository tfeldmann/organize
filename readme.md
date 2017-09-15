# organize

# Usage
```
organize simulate
organize run
organize undo
organize list
organize config
organize --help
organize --version

Arguments:
    simulate        Simulate organizing your files. This allows you to check your rules.
    run             Applies the actions. No simulation.
    undo            Undo the last organization run
    list            List available actions and filters
    config          Open configuration in %{EDITOR}

Options:
    --version       Show program version and exit.
    -h, --help      Show this screen and exit.
```

# Installation

`pip install organize`

# Example config
```
folders:
  - ~/Desktop/Inbox
rules:
  - 'All VDI e-papers go into documents':
    filter: PaperVdi
    action: Move
      dest: ~/Documents/VDI/VDI {year}-{month}-{day}.pdf

  - 'Sort all 1&1 invoices'
    filter: Invoice1and1
    action: Move
      dest: ~/Documents/Invoices/1&1/1&1 {year}-{month}-{day}.pdf
```
