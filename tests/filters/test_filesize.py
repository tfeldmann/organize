from organize.filters import FileSize


def test_constrains_mope1():
    assert not FileSize("<1b,>2b").matches(1)
    assert FileSize(">=1b,<2b").matches(1)
    assert not FileSize(">1.000001b").matches(1)
    assert FileSize("<1.000001B").matches(1)
    assert FileSize("<1.000001").matches(1)
    assert FileSize("<=1,>=0.001kb").matches(1)
    assert FileSize("<1").matches(0)
    assert not FileSize(">1").matches(0)
    assert not FileSize("<1,>1b").matches(0)
    assert FileSize(">99.99999GB").matches(100000000000)
    assert FileSize("0").matches(0)


def test_constrains_base():
    assert FileSize(">1kb,<1kib").matches(1010)
    assert FileSize(">1k,<1ki").matches(1010)
    assert FileSize("1k").matches(1000)
    assert FileSize("1000").matches(1000)


def test_other():
    assert FileSize("<100 Mb").matches(20)
    assert FileSize("<100 Mb, <10 mb, <1 mb, > 0").matches(20)
    assert FileSize(["<100 Mb", ">= 0 Tb"]).matches(20)
