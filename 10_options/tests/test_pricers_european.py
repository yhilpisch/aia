import pytest
import numpy as np
from mcdxa.models import BSM
from mcdxa.payoffs import CallPayoff, PutPayoff, CustomPayoff
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


@pytest.mark.parametrize("opt_type,S0,K", [
    ("call", 80.0, 100.0),
    ("put", 80.0, 100.0),
    ("call", 100.0, 80.0),
    ("put", 100.0, 80.0),
])
def test_european_pricer_custom_plain_vanilla(opt_type, S0, K):
    """
    Test that CustomPayoff can express vanilla call/put and matches analytic BSM for zero volatility.
    """
    T, r, sigma = 1.0, 0.05, 0.0
    model = BSM(r, sigma)
    # define equivalent vanilla payoff via CustomPayoff
    if opt_type == "call":
        func = lambda s: np.maximum(s - K, 0)
    else:
        func = lambda s: np.maximum(K - s, 0)
    payoff = CustomPayoff(func)
    pricer = EuropeanPricer(model, payoff, n_paths=20, n_steps=1, seed=42)
    price_mc, stderr = pricer.price(S0, T, r)
    price_bs = bsm_price(S0, K, T, r, sigma, option_type=opt_type)
    assert stderr == pytest.approx(0.0)
    assert price_mc == pytest.approx(price_bs)
