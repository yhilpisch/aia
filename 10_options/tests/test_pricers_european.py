import pytest

from option_pricing.models import BSM
from option_pricing.payoffs import CallPayoff, PutPayoff
from option_pricing.pricers.european import EuropeanPricer
from option_pricing.analytics import bsm_price


@pytest.mark.parametrize("opt_type", ["call", "put"])
def test_european_pricer_bsm_close_to_analytic(opt_type, rng):
    r, sigma, q = 0.05, 0.2, 0.0
    model = BSM(r=r, sigma=sigma, q=q)
    payoff = CallPayoff(strike=100.0) if opt_type == "call" else PutPayoff(strike=100.0)
    pricer = EuropeanPricer(model, payoff, n_paths=20000, n_steps=1, seed=42)
    price_mc, stderr = pricer.price(S0=100.0, T=1.0, r=r)
    price_an = bsm_price(100.0, 100.0, 1.0, r, sigma, q, option_type=opt_type)
    # MC should be within a few percent of analytic
    assert abs(price_mc - price_an) / price_an < 0.05