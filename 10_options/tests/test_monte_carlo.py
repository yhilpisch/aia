import numpy as np
import pytest

from option_pricing.payoffs import CallPayoff
from option_pricing.models import BSM
from option_pricing.monte_carlo import price_mc


def test_price_mc_bs_call_zero_volatility(rng):
    model = BSM(r=0.1, sigma=0.0, q=0.0)
    payoff = CallPayoff(strike=100.0)
    price, stderr = price_mc(payoff, model,
                             S0=100.0, T=1.0, r=0.1,
                             n_paths=10000, n_steps=1, rng=rng)
    expected = max(100.0 * np.exp(0.1 * 1.0) - 100.0, 0.0)
    assert pytest.approx(price, rel=1e-3) == expected
    assert stderr == pytest.approx(0.0, abs=1e-8)