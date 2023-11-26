import os
from datetime import date, datetime
from typing import Union

import jinja2

# variables that should be always available in a template
BASIC_VARS = dict(
    env=os.environ,
    now=datetime.now,
    utcnow=datetime.utcnow,
    today=date.today,
)


def finalize_placeholder(x):
    # This is used to make the `path` arg available in the filters and actions.
    # If a template uses `path` where no syspath is available this makes it possible
    # to raise an exception.
    if isinstance(x, Exception):
        raise x
    return x


Template = jinja2.Environment(
    variable_start_string="{",
    variable_end_string="}",
    autoescape=False,
    finalize=finalize_placeholder,
    undefined=jinja2.StrictUndefined,
)


def render(template: Union[str, jinja2.environment.Template], args=None) -> str:
    if args is None:
        args = dict()
    if isinstance(template, str):
        text = Template.from_string(template).render(**args, **BASIC_VARS)
    else:
        text = template.render(**args, **BASIC_VARS)

    # expand user and fill environment vars
    text = os.path.expanduser(text)
    text = os.path.expandvars(text)
    return text
