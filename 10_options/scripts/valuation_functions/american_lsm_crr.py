import time
from option_pricing.models import BSM  # Assuming BSM model is used for American option pricing
from option_pricing.payoffs import CallPayoff, PutPayoff
from option_pricing.pricers.american import AmericanBinomialPricer, LongstaffSchwartzPricer


def value_american_lsm_crr(
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
    n_tree: int
):
    """Calculates the American option price using the Longstaff-Schwartz Monte Carlo method and compares it to the Cox-Ross-Rubinstein binomial tree method.

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
        n_tree (int): Number of steps for CRR binomial tree pricing.

    Returns:
        tuple: A tuple containing the Longstaff-Schwartz Monte Carlo price,
               the Monte Carlo standard error, the Cox-Ross-Rubinstein price,
               the absolute error, the percentage error, the Monte Carlo simulation time,
               and the binomial tree method time.
    """
    model = BSM(r, sigma, q=q)  # Assuming BSM model is used for American option pricing
    payoff = CallPayoff(K) if opt_type == "call" else PutPayoff(K)
    am_mc = LongstaffSchwartzPricer(model, payoff, n_paths=n_paths, n_steps=n_steps, seed=seed)
    t0 = time.time()
    price_am_mc, stderr_am = am_mc.price(S0, T, r)
    t_mc_am = time.time() - t0

    am_crr = AmericanBinomialPricer(model, payoff, n_steps=n_tree)
    t0 = time.time()
    price_crr = am_crr.price(S0, T, r)
    t_crr = time.time() - t0

    abs_err = abs(price_am_mc - price_crr)
    pct_err = abs_err / price_crr * 100.0 if price_crr != 0 else float("nan")

    return price_am_mc, stderr_am, price_crr, abs_err, pct_err, t_mc_am, t_crr
