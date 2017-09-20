# organize

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
```
from organize import Rule
from organize import actions, filters


all_rules = [
    Rule(
        filter=filters.PaperVDI(),
        action=actions.Move('~/Documents/VDI Nachrichten/VDI {year}-{month:02}-{day:02}.pdf')
    ),
    Rule(
        filter=filters.Regex(r'^RG(\d{12})-sig\.pdf$'),
        action=actions.Move('~/TF Cloud/Office/Rechnungen/MCF 1und1'),
    ),
    Rule(
        filter=filters.Invoice1and1(),
        action=actions.Move('~/TF Cloud/Office/Rechnungen/{year}-{month:02}-{day:02} 1und1.pdf')
    ),
]

CONFIG = [{
    'folders': [
        '~/Desktop/__Inbox__',
        '~/Download',
        '~/TF Cloud/Office/_EINGANG_'
    ],
    'rules': all_rules,
}]

```
