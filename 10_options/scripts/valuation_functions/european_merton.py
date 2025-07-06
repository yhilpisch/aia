import time
import math
from option_pricing.models import MertonJumpDiffusion
from option_pricing.payoffs import CallPayoff, PutPayoff
from option_pricing.pricers.european import EuropeanPricer
from option_pricing.analytics import merton_price


def value_european_merton(
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
    lam: float,
    mu_j: float,
    sigma_j: float
):
    """Calculates the European option price using Monte Carlo simulation with Merton Jump Diffusion model and compares it to the analytical solution.

    Args:
        S0 (float): Initial stock price.
        K (float): Strike price.
        T (float): Time to maturity.
        r (float): Risk-free rate.
        sigma (float): Volatility.
        opt_type (str): Option type ('call' or 'put').
        n_paths (int): Number of Monte Carlo paths.
        n_steps (int): Number of time steps per path.
        seed (int): Random seed for Monte Carlo simulation.
        q (float): Dividend yield.
        lam (float): Jump intensity (lambda) for Merton jump-diffusion.
        mu_j (float): Mean jump size (lognormal mu_j) for Merton model.
        sigma_j (float): Jump size volatility (sigma_j) for Merton model.

    Returns:
        tuple: A tuple containing the Monte Carlo price, the Monte Carlo standard error,
               the analytical price, the absolute error, the percentage error,
               and the Monte Carlo simulation time.
    """
    model_mjd = MertonJumpDiffusion(r, sigma, lam, mu_j, sigma_j, q=q)
    payoff = CallPayoff(K) if opt_type == "call" else PutPayoff(K)
    mjd_mc = EuropeanPricer(model_mjd, payoff, n_paths=n_paths, n_steps=n_steps, seed=seed)
    t0 = time.time()
    price_mc_jd, stderr_jd = mjd_mc.price(S0, T, r)
    t_mc_jd = time.time() - t0

    price_call_jd = merton_price(S0, K, T, r, sigma, lam, mu_j, sigma_j, q=q)
    if opt_type == 'call':
        price_anal_jd = price_call_jd
    else:
        price_anal_jd = price_call_jd - S0 * math.exp(-q*T) + K * math.exp(-r*T)

    abs_err_jd = abs(price_mc_jd - price_anal_jd)
    pct_err_jd = abs_err_jd / price_anal_jd * 100.0 if price_anal_jd != 0 else float(nan)

    return price_mc_jd, stderr_jd, price_anal_jd, abs_err_jd, pct_err_jd, t_mc_jd
