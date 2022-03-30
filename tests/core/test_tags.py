from organize.core import should_execute


def test_tags():
    assert should_execute(rule_tags=[], tags=[], skip_tags=[])
    assert should_execute(rule_tags=["anything"], tags=[], skip_tags=[])
    assert should_execute(rule_tags=["always"], tags=["debug", "test"], skip_tags=[])
    assert not should_execute(rule_tags=[], tags=["debug", "test"], skip_tags=[])
    assert not should_execute(rule_tags=["test"], tags=["debug"], skip_tags=["test"])
    assert not should_execute(rule_tags=["never"], tags=[], skip_tags=[])
