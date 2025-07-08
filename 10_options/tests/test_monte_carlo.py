
import numpy as np
import pytest

from option_pricing.monte_carlo import price_mc
from option_pricing.models import BSM
from option_pricing.payoffs import CallPayoff


def test_price_mc_zero_volatility():
    model = BSM(r=0.05, sigma=0.0, q=0.0)
    payoff = CallPayoff(strike=100.0)
    # With zero volatility, the payoff is deterministic and matches BSM analytic
    price, stderr = price_mc(payoff, model, S0=100.0, T=1.0, r=0.05, n_paths=50, n_steps=1)
    from option_pricing.analytics import bsm_price
    expected = bsm_price(100.0, 100.0, 1.0, 0.05, 0.0, option_type='call')
    assert stderr == pytest.approx(0.0, abs=1e-12)
    assert price == pytest.approx(expected, rel=1e-6)


def test_price_mc_in_the_money():
    model = BSM(r=0.0, sigma=0.0, q=0.0)
    payoff = CallPayoff(strike=50.0)
    price, stderr = price_mc(payoff, model, S0=100.0, T=1.0, r=0.0, n_paths=10, n_steps=1)
    # deterministic S=100, payoff=50, no discount
    assert stderr == 0.0
    assert price == pytest.approx(50.0)
