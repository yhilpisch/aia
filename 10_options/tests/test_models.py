import numpy as np
import math
import pytest

from mcdxa.models import BSM, Heston, MertonJumpDiffusion


def test_bsm_deterministic_growth():
    model = BSM(r=0.05, sigma=0.0, q=0.0)
    paths = model.simulate(S0=100.0, T=1.0, n_paths=3, n_steps=4)
    # With zero volatility and zero dividend, S = S0 * exp(r * t)
    t_grid = np.linspace(0, 1.0, 5)
    expected = 100.0 * np.exp(0.05 * t_grid)
    for p in paths:
        assert np.allclose(p, expected)


def test_heston_nonnegative_and_shape():
    model = Heston(r=0.03, kappa=1.0, theta=0.04, xi=0.2, rho=0.0, v0=0.04, q=0.0)
    paths = model.simulate(S0=100.0, T=1.0, n_paths=10, n_steps=5)
    assert paths.shape == (10, 6)
    assert np.all(paths >= 0)


def test_mjd_jump_effect():
    # With high jump intensity and zero diffusion, expect jumps
    model = MertonJumpDiffusion(r=0.0, sigma=0.0, lam=10.0, mu_j=0.0, sigma_j=0.0, q=0.0)
    paths = model.simulate(S0=1.0, T=1.0, n_paths=1000, n_steps=1)
    # With zero jump size variance and mu_j=0, jumps yield Y=1, so S should equal S0
    assert paths.shape == (1000, 2)
    assert np.allclose(paths[:, -1], 1.0)
