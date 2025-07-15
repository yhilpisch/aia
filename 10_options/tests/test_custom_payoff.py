import numpy as np
import pytest

from mcdxa.payoffs import CustomPayoff


def test_custom_payoff_requires_callable():
    with pytest.raises(TypeError):
        CustomPayoff(123)


@pytest.mark.parametrize("values, K, func, expected", [
    # call-style: max(sqrt(S) - K, 0)
    (np.array([0, 1, 4, 9, 16]), 3,
     lambda s: np.maximum(np.sqrt(s) - 3, 0),
     np.maximum(np.sqrt(np.array([0, 1, 4, 9, 16])) - 3, 0)),
    # put-style: max(K - sqrt(S), 0)
    (np.array([0, 1, 4, 9, 16]), 3,
     lambda s: np.maximum(3 - np.sqrt(s), 0),
     np.maximum(3 - np.sqrt(np.array([0, 1, 4, 9, 16])), 0)),
])
def test_custom_payoff_terminal(values, K, func, expected):
    payoff = CustomPayoff(func)
    result = payoff(values)
    assert np.allclose(result, expected)


def test_custom_payoff_on_paths():
    # values as paths: terminal prices in last column
    paths = np.array([[1, 4, 9], [16, 25, 36]])
    K = 5
    payoff = CustomPayoff(lambda s: np.maximum(np.sqrt(s) - K, 0))
    # terminal prices are 9 and 36
    expected = np.maximum(np.sqrt(np.array([9, 36])) - 5, 0)
    result = payoff(paths)
    assert np.allclose(result, expected)
