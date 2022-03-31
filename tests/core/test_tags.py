from organize.core import should_execute


def test_no_tags_given():
    assert should_execute(rule_tags=None, tags=None, skip_tags=None)
    assert should_execute(rule_tags=["tag"], tags=None, skip_tags=None)
    assert should_execute(rule_tags=["tag", "tag2"], tags=None, skip_tags=None)


def test_run_tagged():
    assert not should_execute(rule_tags=None, tags=["tag"], skip_tags=None)
    assert should_execute(rule_tags=["tag"], tags=["tag"], skip_tags=None)
    assert should_execute(rule_tags=["tag", "tag2"], tags=["tag"], skip_tags=None)
    assert not should_execute(rule_tags=["foo", "bar"], tags=["tag"], skip_tags=None)
    assert not should_execute(rule_tags=["taggity"], tags=["tag"], skip_tags=None)


def test_skip():
    assert should_execute(rule_tags=None, tags=None, skip_tags=["tag"])
    assert should_execute(rule_tags=["tag"], tags=None, skip_tags=["asd"])
    assert not should_execute(rule_tags=["tag"], tags=None, skip_tags=["tag"])
    assert not should_execute(rule_tags=["tag", "tag2"], tags=None, skip_tags=["tag"])


def test_combination():
    assert not should_execute(rule_tags=None, tags=["tag"], skip_tags=["foo"])
    assert not should_execute(rule_tags=["foo", "tag"], tags=["tag"], skip_tags=["foo"])


def test_always():
    assert should_execute(rule_tags=["always"], tags=["debug", "test"], skip_tags=None)
    assert should_execute(rule_tags=["always", "tag"], tags=None, skip_tags=["tag"])
    # skip only if specifically requested
    assert not should_execute(
        rule_tags=["always", "tag"], tags=None, skip_tags=["always"]
    )


def test_never():
    assert not should_execute(rule_tags=["never"], tags=None, skip_tags=None)
    assert not should_execute(rule_tags=["never", "tag"], tags=["tag"], skip_tags=None)
    # run only if specifically requested
    assert should_execute(rule_tags=["never", "tag"], tags=["never"], skip_tags=None)
