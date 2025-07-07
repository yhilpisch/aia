import numpy as np
import pytest

from option_pricing.models import BSM
from option_pricing.payoffs import CallPayoff, PutPayoff
from option_pricing.pricers.american import AmericanBinomialPricer, LongstaffSchwartzPricer
from option_pricing.analytics import bsm_price


def test_american_binomial_pricer_call_equals_european(rng):
    r, sigma, q = 0.05, 0.2, 0.0
    model = BSM(r=r, sigma=sigma, q=q)
    payoff = CallPayoff(strike=100.0)
    pricer = AmericanBinomialPricer(model, payoff, n_steps=50)
    price_am = pricer.price(100.0, 1.0, r)
    price_eu = bsm_price(100.0, 100.0, 1.0, r, sigma, q, option_type="call")
    assert abs(price_am - price_eu) / price_eu < 0.02


def test_american_binomial_pricer_put_exercise_benefit(rng):
    r, sigma, q = 0.05, 0.2, 0.0
    model = BSM(r=r, sigma=sigma, q=q)
    payoff = PutPayoff(strike=100.0)
    pricer = AmericanBinomialPricer(model, payoff, n_steps=50)
    price_am = pricer.price(100.0, 1.0, r)
    price_eu = bsm_price(100.0, 100.0, 1.0, r, sigma, q, option_type="put")
    assert price_am >= price_eu


@pytest.mark.parametrize("n_paths,n_steps", [(5000,10), (10000,20)])
def test_longstaff_schwartz_pricer_put_positive(rng, n_paths, n_steps):
    r, sigma, q = 0.05, 0.2, 0.02
    model = BSM(r=r, sigma=sigma, q=q)
    payoff = PutPayoff(strike=100.0)
    pricer = LongstaffSchwartzPricer(model, payoff, n_paths=n_paths, n_steps=n_steps, seed=42)
    price_ls, stderr = pricer.price(100.0, 1.0, r)
    assert price_ls > 0.0
    assert stderr >= 0.0