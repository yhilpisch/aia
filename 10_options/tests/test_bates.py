import math

import numpy as np
import pytest

from option_pricing.models import Bates
from option_pricing.bates import simulate_bates, bates_price
from option_pricing.analytics import heston_price


def test_simulate_bates_shape_and_values():
    # basic shape and initial value
    rng = np.random.default_rng(123)
    paths = simulate_bates(
        S0=100.0, T=1.0, r=0.05,
        kappa=2.0, theta=0.04, xi=0.2, rho=0.0, v0=0.02,
        lam=0.3, mu_j=-0.1, sigma_j=0.2, q=0.0,
        n_paths=5, n_steps=3, rng=rng
    )
    # Expect shape (n_paths, n_steps+1)
    assert paths.shape == (5, 4)
    # initial column should equal S0
    assert np.allclose(paths[:, 0], 100.0)


@pytest.mark.parametrize("opt_type", ["call", "put"])
def test_bates_price_zero_jumps_equals_heston(opt_type):
    # When lam=0, Bates reduces to Heston model
    S0, K, T, r = 100.0, 100.0, 1.0, 0.05
    kappa, theta, xi, rho, v0 = 2.0, 0.04, 0.2, -0.5, 0.03
    # zero jumps
    p_bates = bates_price(
        S0, K, T, r,
        kappa, theta, xi, rho, v0,
        lam=0.0, mu_j=-0.1, sigma_j=0.2,
        q=0.0, option_type=opt_type
    )
    p_heston = heston_price(
        S0, K, T, r,
        kappa, theta, xi, rho, v0,
        q=0.0, option_type=opt_type
    )
    assert p_bates == pytest.approx(p_heston, rel=1e-7)


def test_bates_put_call_parity():
    # Test put-call parity for Bates
    S0, K, T, r = 100.0, 100.0, 1.0, 0.03
    params = dict(
        kappa=1.5, theta=0.05, xi=0.3, rho=0.0, v0=0.04,
        lam=0.2, mu_j=-0.05, sigma_j=0.15, q=0.0,
    )
    call = bates_price(S0, K, T, r, **params, option_type="call")
    put = bates_price(S0, K, T, r, **params, option_type="put")
    # Parity: call - put = S0*exp(-qT) - K*exp(-rT)
    expected = S0 * math.exp(-params['q'] * T) - K * math.exp(-r * T)
    assert (call - put) == pytest.approx(expected, rel=1e-7)
