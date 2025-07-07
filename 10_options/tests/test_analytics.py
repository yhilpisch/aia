import numpy as np
import pytest

from option_pricing.analytics import bsm_price, merton_price, heston_price, bcc_price


def test_bsm_put_call_parity():
    call = bsm_price(100.0, 100.0, 1.0, 0.05, 0.2, 0.0, option_type="call")
    put = bsm_price(100.0, 100.0, 1.0, 0.05, 0.2, 0.0, option_type="put")
    forward = 100.0 * np.exp(-0.0 * 1.0)
    pv_strike = 100.0 * np.exp(-0.05 * 1.0)
    assert pytest.approx(call - put, rel=1e-8) == forward - pv_strike


@pytest.mark.parametrize("func,params", [
    (merton_price, (100.0, 100.0, 1.0, 0.05, 0.2, 0.3, -0.1, 0.2, 0.0)),
    (heston_price, (100.0, 100.0, 1.0, 0.05, 0.0, 2.0, 0.04, 0.2, -0.5, 0.02)),
    (bcc_price,   (100.0, 100.0, 1.0, 0.05, 0.0, 2.0, 0.04, 0.2, -0.5, 0.02, 0.3, -0.1, 0.2)),
])
def test_analytics_prices_non_negative(func, params):
    price = func(*params, option_type="call")
    assert price >= 0.0