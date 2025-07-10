import pytest
from mcdxa.models import BSM
from mcdxa.payoffs import CallPayoff, PutPayoff
from mcdxa.pricers.european import EuropeanPricer
from mcdxa.analytics import bsm_price


@pytest.mark.parametrize("opt_type", ["call", "put"])
def test_european_pricer_matches_bsm(opt_type):
    S0, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.0
    model = BSM(r, sigma)
    payoff = CallPayoff(K) if opt_type == "call" else PutPayoff(K)
    pricer = EuropeanPricer(model, payoff, n_paths=20, n_steps=1, seed=42)
    price_mc, stderr = pricer.price(S0, T, r)
    price_bs = bsm_price(S0, K, T, r, sigma, option_type=opt_type)
    # Zero volatility: MC should produce deterministic result equal to analytic
    assert stderr == pytest.approx(0.0)
    assert price_mc == pytest.approx(price_bs)
