import numpy as np

from ..monte_carlo import price_mc


class EuropeanPricer:
    """
    Monte Carlo pricer for European options.

    Attributes:
        model: Asset price model with simulate method.
        payoff: Payoff callable.
        n_paths (int): Number of simulation paths.
        n_steps (int): Number of time steps per path.
        rng: numpy random generator.
    """
    def __init__(self, model, payoff, n_paths: int = 100_000,
                 n_steps: int = 1, seed: int = None):
        self.model = model
        self.payoff = payoff
        self.n_paths = n_paths
        self.n_steps = n_steps
        self.rng = None if seed is None else np.random.default_rng(seed)

    def price(self, S0: float, T: float, r: float) -> tuple:
        """
        Price the option via Monte Carlo simulation.

        Args:
            S0 (float): Initial asset price.
            T (float): Time to maturity.
            r (float): Risk-free rate.

        Returns:
            tuple: (price, stderr)
        """
        return price_mc(self.payoff, self.model, S0, T, r,
                        self.n_paths, self.n_steps, rng=self.rng)