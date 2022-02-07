from organize.filters import Size


def test_constrains_mope1():
    assert not Size("<1b,>2b").matches(1)
    assert Size(">=1b,<2b").matches(1)
    assert not Size(">1.000001b").matches(1)
    assert Size("<1.000001B").matches(1)
    assert Size("<1.000001").matches(1)
    assert Size("<=1,>=0.001kb").matches(1)
    assert Size("<1").matches(0)
    assert not Size(">1").matches(0)
    assert not Size("<1,>1b").matches(0)
    assert Size(">99.99999GB").matches(100000000000)
    assert Size("0").matches(0)


def test_constrains_base():
    assert Size(">1kb,<1kib").matches(1010)
    assert Size(">1k,<1ki").matches(1010)
    assert Size("1k").matches(1000)
    assert Size("1000").matches(1000)


def test_other():
    assert Size("<100 Mb").matches(20)
    assert Size("<100 Mb, <10 mb, <1 mb, > 0").matches(20)
    assert Size(["<100 Mb", ">= 0 Tb"]).matches(20)
