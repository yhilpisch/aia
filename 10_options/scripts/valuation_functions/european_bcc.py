import time
import numpy as np
from option_pricing.models import BCCModel
from option_pricing.payoffs import CallPayoff, PutPayoff
from option_pricing.pricers.european import EuropeanPricer
from option_pricing.analytics import bcc_price

def value_european_bcc(
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    opt_type: str,
    n_paths: int,
    n_steps: int,
    seed: int,
    q: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    v0: float,
    lam: float,
    mu_j: float,
    sigma_j: float
):
    """
    Calculates the European option price using Monte Carlo simulation under the
    Bates model (Heston SV + Merton jumps) and compares it to the Lewis-CF analytic price.

    Args:
        S0 (float): Initial asset price.
        K (float): Strike price.
        T (float): Time to maturity.
        r (float): Risk-free rate.
        sigma (float): Unused (for compatibility).
        opt_type (str): 'call' or 'put'.
        n_paths (int): Number of Monte Carlo paths.
        n_steps (int): Number of time steps per path.
        seed (int): Random seed.
        q (float): Dividend yield.
        kappa (float): Heston mean-reversion speed.
        theta (float): Heston long-run variance.
        xi (float): Heston vol-of-vol.
        rho (float): Correlation in Heston.
        v0 (float): Initial Heston variance.
        lam (float): Jump intensity (Poisson rate).
        mu_j (float): Mean of log jump size.
        sigma_j (float): Std dev of log jump size.

    Returns:
        tuple: (mc_price, mc_stderr, analytic_price, abs_err, pct_err, mc_time)
    """
    model = BCCModel(
        r, kappa, theta, xi, rho, v0,
        lam, mu_j, sigma_j,
        q=q
    )
    payoff = CallPayoff(K) if opt_type == 'call' else PutPayoff(K)
    pricer = EuropeanPricer(model, payoff, n_paths=n_paths, n_steps=n_steps, seed=seed)
    t0 = time.time()
    price_mc, stderr = pricer.price(S0, T, r)
    t_mc = time.time() - t0

    price_an = bcc_price(
        S0, K, T, r, q,
        kappa, theta, xi, rho, v0,
        lam, mu_j, sigma_j,
        option_type=opt_type,
        integration_limit=2000.0
    )

    abs_err = abs(price_mc - price_an)
    pct_err = abs_err / price_an * 100.0 if price_an != 0 else float('nan')
    return price_mc, stderr, price_an, abs_err, pct_err, t_mc