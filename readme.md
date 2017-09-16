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
RULES:
  - folder:
    - "~/Desktop/Inbox"
    - "~/Documents"
    rules:  
    - name: "VDI Nachrichten"
      filter: PaperVdi()
      action: Move("~/Documents/VDI/VDI {year}-{month}-{day}.pdf")

    - name: "1und1 Rechnungen"
      filter: Invoice1and1()
      action: Move("~/Documents/Invoices/1&1/1&1 {year}-{month}-{day}.pdf")
```
