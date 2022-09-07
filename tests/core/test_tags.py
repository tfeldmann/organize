import pytest
from organize.core import should_execute


@pytest.mark.parametrize(
    "result, rule_tags, tags, skip_tags",
    (
        # no tags given
        (True, None, None, None),
        (True, ["tag"], None, None),
        (True, ["tag", "tag2"], None, None),
        # run tagged
        (False, None, ["tag"], None),
        (True, ["tag"], ["tag"], None),
        (True, ["tag", "tag2"], ["tag"], None),
        (False, ["foo", "bar"], ["tag"], None),
        (False, ["taggity"], ["tag"], None),
        # skip
        (True, None, None, ["tag"]),
        (True, ["tag"], None, ["asd"]),
        (False, ["tag"], None, ["tag"]),
        (False, ["tag", "tag2"], None, ["tag"]),
        # combination
        (False, None, ["tag"], ["foo"]),
        (False, ["foo", "tag"], ["tag"], ["foo"]),
        # always
        (True, ["always"], ["debug", "test"], None),
        (True, ["always", "tag"], None, ["tag"]),
        # skip only if specifically requested
        (False, ["always", "tag"], None, ["always"]),
        # never
        (False, ["never"], None, None),
        (False, ["never", "tag"], ["tag"], None),
        # run only if specifically requested
        (True, ["never", "tag"], ["never"], None),
    ),
)
def test_tags(result, rule_tags, tags, skip_tags):
    assert should_execute(rule_tags=rule_tags, tags=tags, skip_tags=skip_tags) == result
