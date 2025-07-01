import numpy as np


def price_mc(payoff, model, S0: float, T: float, r: float,
             n_paths: int, n_steps: int = 1,
             rng: np.random.Generator = None) -> tuple:
    """
    Generic Monte Carlo pricer.

    Args:
        payoff (callable): Payoff function on terminal prices.
        model: Model instance with a simulate method.
        S0 (float): Initial asset price.
        T (float): Time to maturity.
        r (float): Risk-free rate.
        n_paths (int): Number of Monte Carlo paths.
        n_steps (int): Number of time steps per path.
        rng (np.random.Generator, optional): Random generator.

    Returns:
        price (float): Discounted Monte Carlo price.
        stderr (float): Standard error of the estimate.
    """
    paths = model.simulate(S0, T, n_paths, n_steps, rng=rng)
    ST = paths[:, -1]
    payoffs = payoff(ST)
    discounted = np.exp(-r * T) * payoffs
    price = discounted.mean()
    stderr = discounted.std(ddof=1) / np.sqrt(n_paths)
    return price, stderr