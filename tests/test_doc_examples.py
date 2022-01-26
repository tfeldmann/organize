import re

import fs

from organize.config import load_from_string, CONFIG_SCHEMA

RE_CONFIG = re.compile(r"```yaml\n(?P<config>rules:(?:.*?\n)+?)```", re.MULTILINE)


DOCS = (
    "03-filters.md",
    "04-actions.md",
)

docdir = fs.open_fs("docs")
for f in DOCS:
    text = docdir.readtext(f)
    for match in RE_CONFIG.findall(text):
        try:
            config = load_from_string(match)
            CONFIG_SCHEMA.validate(config)
        except Exception as e:
            print("invalid config: ")
            print(match)
            print(str(e))
