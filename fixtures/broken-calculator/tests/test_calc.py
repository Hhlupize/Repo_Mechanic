from calc import add, sub, mul, div
import pytest


def test_add():
    assert add(2, 3) == 5


def test_sub():
    assert sub(5, 2) == 3


def test_mul():
    assert mul(4, 6) == 24


def test_div():
    with pytest.raises(ZeroDivisionError):
        _ = div(1, 0)

