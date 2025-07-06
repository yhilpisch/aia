import time
from option_pricing.models import BSM
from option_pricing.payoffs import CallPayoff, PutPayoff
from option_pricing.pricers.european import EuropeanPricer
from option_pricing.analytics import bsm_price


def value_european_bsm(
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    opt_type: str,
    n_paths: int,
    n_steps: int,
    seed: int,
    q: float
):
    """Calculates the European option price using Monte Carlo simulation and compares it to the Black-Scholes model.

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

    Returns:
        tuple: A tuple containing the Monte Carlo price, the Monte Carlo standard error,
               the Black-Scholes price, the absolute error, the percentage error,
               and the Monte Carlo simulation time.
    """
    model = BSM(r, sigma, q=q)
    payoff = CallPayoff(K) if opt_type == "call" else PutPayoff(K)
    eur_mc = EuropeanPricer(model, payoff, n_paths=n_paths, n_steps=n_steps, seed=seed)
    t0 = time.time()
    price_mc, stderr = eur_mc.price(S0, T, r)
    t_mc = time.time() - t0

    # Analytical BSM price, including dividend yield
    price_bs = bsm_price(S0, K, T, r, sigma, q, option_type=opt_type)

    abs_err = abs(price_mc - price_bs)
    pct_err = abs_err / price_bs * 100.0 if price_bs != 0 else float("nan")

    return price_mc, stderr, price_bs, abs_err, pct_err, t_mc

