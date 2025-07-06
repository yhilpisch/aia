import time
from option_pricing.models import Heston
from option_pricing.payoffs import CallPayoff, PutPayoff
from option_pricing.pricers.european import EuropeanPricer
from option_pricing.analytics import heston_price


def value_european_heston(
    S0: float,
    K: float,
    T: float,
    r: float,
    opt_type: str,
    n_paths: int,
    n_steps: int,
    seed: int,
    q: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    v0: float
):
    """Calculates the European option price using Monte Carlo simulation with Heston model and compares it to the semi-analytical solution.

    Args:
        S0 (float): Initial stock price.
        K (float): Strike price.
        T (float): Time to maturity.
        r (float): Risk-free rate.
        opt_type (str): Option type ('call' or 'put').
        n_paths (int): Number of Monte Carlo paths.
        n_steps (int): Number of time steps per path.
        seed (int): Random seed for Monte Carlo simulation.
        q (float): Dividend yield.
        kappa (float): Mean-reversion speed for Heston model.
        theta (float): Long-run variance theta for Heston model.
        xi (float): Vol-of-vol xi for Heston model.
        rho (float): Correlation rho for Heston model.
        v0 (float): Initial variance v0 for Heston model.

    Returns:
        tuple: A tuple containing the Monte Carlo price, the Monte Carlo standard error,
               the semi-analytical price, the absolute error, the percentage error,
               and the Monte Carlo simulation time.
    """
    model_hes = Heston(r, kappa, theta, xi, rho, v0, q=q)
    payoff = CallPayoff(K) if opt_type == "call" else PutPayoff(K)
    hes_mc = EuropeanPricer(model_hes, payoff, n_paths=n_paths, n_steps=n_steps, seed=seed)
    t0 = time.time()
    price_mc_hes, stderr_hes = hes_mc.price(S0, T, r)
    t_mc_hes = time.time() - t0

    price_an_hes = heston_price(
        S0, K, T, r, q, kappa, theta, xi, rho, v0, option_type=opt_type
    )

    abs_err = abs(price_mc_hes - price_an_hes)
    pct_err = abs_err / price_an_hes * 100.0 if price_an_hes != 0 else float(nan)

    return price_mc_hes, stderr_hes, price_an_hes, abs_err, pct_err, t_mc_hes
