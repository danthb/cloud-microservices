
import math
import pytest

from src.val import add, subtract, multiply, divide


def test_add():
    assert add(1, 2) == 3
    assert add(-1, 2) == 1
    assert add(0, 0) == 0


def test_subtract():
    assert subtract(3, 2) == 1
    assert subtract(-1, 2) == -3
    assert subtract(0, 0) == 0


def test_multiply():
    assert multiply(3, 2) == 6
    assert multiply(-1, 2) == -2
    assert multiply(0, 5) == 0


def test_divide():
    assert divide(4, 2) == 2
    assert math.isclose(divide(3, 2),1.5,rel_tol=1e-9)
    assert divide(1, 3) == 1/3
    assert divide(0, 5) == 0
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)