from kolmo_stats import mean
import pytest


def test_mean_basic():
    assert mean([1, 2, 3]) == 2.0

def test_mean_single():
    assert mean([5]) == 5.0

def test_mean_floats():
    assert mean([1.5, 2.5]) == 2.0

def test_mean_empty_raises():
    with pytest.raises(ValueError):
        mean([])
