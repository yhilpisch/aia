import pytest
import numpy as np

from mcdxa.models import BSM
from mcdxa.payoffs import CallPayoff, PutPayoff
from mcdxa.pricers.american import AmericanBinomialPricer, LongstaffSchwartzPricer


@pytest.fixture(autouse=True)
def fix_seed(monkeypatch):
    import numpy as np
    rng = np.random.default_rng(12345)
    monkeypatch.setattr(np.random, 'default_rng', lambda *args, **kwargs: rng)


def test_crr_binomial_call_no_dividend_intrinsic():
    model = BSM(r=0.05, sigma=0.0, q=0.0)
    K, S0, T = 100.0, 110.0, 1.0
    payoff = CallPayoff(K)
    pricer = AmericanBinomialPricer(model, payoff, n_steps=10)
    price = pricer.price(S0, T, r=0.05)
    assert price == pytest.approx(S0 - K)


def test_lsm_put_no_volatility_exercise():
    model = BSM(r=0.0, sigma=0.0, q=0.0)
    K, S0, T = 100.0, 90.0, 1.0
    payoff = PutPayoff(K)
    pricer = LongstaffSchwartzPricer(
        model, payoff, n_paths=50, n_steps=5, seed=42)
    price, stderr = pricer.price(S0, T, r=0.0)
    # Zero vol: always exercise immediately, price equals intrinsic
    assert stderr == pytest.approx(0.0)
    assert price == pytest.approx(K - S0)
