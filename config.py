from organize import Rule
from organize import actions, filters

__all__ = ['CONFIG']


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
