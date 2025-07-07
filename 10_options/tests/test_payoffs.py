import numpy as np

from option_pricing.payoffs import (
    CallPayoff, PutPayoff,
    AsianCallPayoff, AsianPutPayoff,
    LookbackCallPayoff, LookbackPutPayoff,
)


def test_call_put_payoffs():
    S = np.array([90.0, 100.0, 110.0])
    call = CallPayoff(strike=100.0)
    put = PutPayoff(strike=100.0)
    assert np.allclose(call(S), [0.0, 0.0, 10.0])
    assert np.allclose(put(S), [10.0, 0.0, 0.0])


def test_asian_payoffs():
    S = np.array([[100.0, 110.0, 120.0], [80.0, 90.0, 100.0]])
    asian_call = AsianCallPayoff(strike=100.0)
    asian_put = AsianPutPayoff(strike=100.0)
    avg = S.mean(axis=1)
    expected_call = np.maximum(avg - 100.0, 0.0)
    expected_put = np.maximum(100.0 - avg, 0.0)
    assert np.allclose(asian_call(S), expected_call)
    assert np.allclose(asian_put(S), expected_put)


def test_lookback_payoffs():
    S = np.array([[100.0, 120.0, 110.0], [100.0, 80.0, 90.0]])
    lookback_call = LookbackCallPayoff(strike=100.0)
    lookback_put = LookbackPutPayoff(strike=100.0)
    high = S.max(axis=1)
    low = S.min(axis=1)
    expected_call = np.maximum(high - 100.0, 0.0)
    expected_put = np.maximum(100.0 - low, 0.0)
    assert np.allclose(lookback_call(S), expected_call)
    assert np.allclose(lookback_put(S), expected_put)