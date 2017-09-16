from organize import Rule
from organize import actions, filters

__all__ = ['CONFIG']


all_rules = [
    Rule(
        filter=filters.PaperVDI(),
        action=actions.Move('~/Documents/VDI Nachrichten/VDI {year}-{month:02}-{day:02}.pdf')),
    Rule(
        filter=filters.Invoice1and1(),
        action=actions.Move('~/TF Cloud/Office/Rechnungen/1und1 {year}-{month:02}-{day:02}.pdf')),
]


CONFIG = [{
    'folder': ['~/Desktop/__Inbox__', '~/Download'],
    'rules': all_rules,
}]
