from organize.output.changedetector import ChangeDetector


def test_changed():
    d = ChangeDetector()
    assert d.changed(1)
    assert not d.changed(1)
    assert not d.changed(1)
    d.reset()
    assert d.changed(1)
    assert d.changed(2)
