import numpy as np
import pytest

from mcdxa.payoffs import (
    CallPayoff, PutPayoff,
    AsianCallPayoff, AsianPutPayoff,
    LookbackCallPayoff, LookbackPutPayoff,
)


@pytest.mark.parametrize("payoff_cls, spot, strike, expected", [
    (CallPayoff, np.array([50, 100, 150]), 100, np.array([0, 0, 50])),
    (PutPayoff, np.array([50, 100, 150]), 100, np.array([50, 0, 0])),
])
def test_vanilla_payoff(payoff_cls, spot, strike, expected):
    payoff = payoff_cls(strike)
    result = payoff(spot)
    assert np.allclose(result, expected)


@pytest.mark.parametrize("payoff_cls, path, expected", [
    (AsianCallPayoff, np.array([[1, 3, 5], [2, 2, 2]]), np.array([max((1+3+5)/3 - 3, 0), max((2+2+2)/3 - 3, 0)])),
    (AsianPutPayoff, np.array([[1, 3, 5], [2, 2, 2]]), np.array([max(3 - (1+3+5)/3, 0), max(3 - (2+2+2)/3, 0)])),
    (LookbackCallPayoff, np.array([[1, 4], [3, 2]]), np.array([max(4-2, 0), max(3-2, 0)])),
    (LookbackPutPayoff, np.array([[1, 4], [3, 2]]), np.array([max(2-1, 0), max(2-3, 0)])),
])
def test_path_payoff(payoff_cls, path, expected):
    strike = 3 if 'Asian' in payoff_cls.__name__ else 2
    payoff = payoff_cls(strike)
    result = payoff(path)
    assert np.allclose(result, expected)
