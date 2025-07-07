import numpy as np
import pytest

from option_pricing.models import BSM, Heston, MertonJumpDiffusion, BCCModel


def test_bsm_simulate_shape_and_deterministic(rng):
    model = BSM(r=0.05, sigma=0.0, q=0.0)
    paths = model.simulate(S0=100.0, T=1.0, n_paths=10, n_steps=5, rng=rng)
    assert paths.shape == (10, 6)
    expected = 100.0 * np.exp(0.05 * 1.0)
    assert np.allclose(paths[:, -1], expected)


def test_merton_jump_diffusion_no_jumps(rng):
    model = MertonJumpDiffusion(r=0.05, sigma=0.0, lam=0.0, mu_j=0.0, sigma_j=0.0, q=0.0)
    paths = model.simulate(S0=100.0, T=1.0, n_paths=10, n_steps=5, rng=rng)
    assert paths.shape == (10, 6)
    expected = 100.0 * np.exp(0.05 * 1.0)
    assert np.allclose(paths[:, -1], expected)


def test_heston_simulate_zero_volatility(rng):
    model = Heston(r=0.05, kappa=1.0, theta=0.04, xi=0.0, rho=0.0, v0=0.0, q=0.0)
    paths = model.simulate(S0=100.0, T=1.0, n_paths=10, n_steps=5, rng=rng)
    assert paths.shape == (10, 6)
    expected = 100.0 * np.exp(0.05 * 1.0)
    assert np.allclose(paths[:, -1], expected)


def test_bcc_simulate_no_variance_or_jumps(rng):
    model = BCCModel(r=0.05, kappa=1.0, theta=0.04, xi=0.0, rho=0.0,
                     v0=0.0, lam=0.0, mu_j=0.0, sigma_j=0.0, q=0.0)
    paths = model.simulate(S0=100.0, T=1.0, n_paths=10, n_steps=5, rng=rng)
    assert paths.shape == (10, 6)
    expected = 100.0 * np.exp(0.05 * 1.0)
    assert np.allclose(paths[:, -1], expected)