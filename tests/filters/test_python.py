from organize.filters import Python


def test_basic():
    p = Python(
        """
        return "some-string"
        """
    )
    result = p.run()
    assert result.matches
    assert result.updates == {"python": "some-string"}
