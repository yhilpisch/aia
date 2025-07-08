import math
import numpy as np


class AmericanBinomialPricer:
    """
    Cox-Ross-Rubinstein binomial pricer for American options.

    Attributes:
        model: Asset price model with attributes r, sigma, q.
        payoff: Payoff callable.
        n_steps: Number of binomial steps.
    """
    def __init__(self, model, payoff, n_steps: int = 200):
        self.model = model
        self.payoff = payoff
        self.n_steps = n_steps

    def price(self, S0: float, T: float, r: float) -> float:
        """
        Price the American option using the CRR binomial model.

        Args:
            S0 (float): Initial asset price.
            T (float): Time to maturity.
            r (float): Risk-free rate.

        Returns:
            float: American option price.
        """
        sigma = self.model.sigma
        # degenerate zero-volatility American: immediate exercise intrinsic
        if sigma <= 0 or T <= 0:
            return float(self.payoff(S0))
        q = getattr(self.model, 'q', 0.0)
        n = self.n_steps
        dt = T / n
        u = math.exp(sigma * math.sqrt(dt))
        d = 1 / u
        disc = math.exp(-r * dt)
        # risk-neutral probability
        p = (math.exp((r - q) * dt) - d) / (u - d)

        # asset prices at maturity
        prices = [S0 * (u ** (n - j)) * (d ** j) for j in range(n + 1)]
        # option values at maturity
        values = [float(self.payoff(price)) for price in prices]

        # backward induction
        for i in range(n - 1, -1, -1):
            for j in range(i + 1):
                cont = disc * (p * values[j] + (1 - p) * values[j + 1])
                exercise = float(self.payoff(S0 * (u ** (i - j)) * (d ** j)))
                values[j] = max(exercise, cont)
        return values[0]


class LongstaffSchwartzPricer:
    """
    Longstaff-Schwartz least-squares Monte Carlo pricer for American options.

    Attributes:
        model: Asset price model with simulate method.
        payoff: Payoff callable (vectorized).
        n_paths: Number of Monte Carlo paths.
        n_steps: Number of time steps per path.
        rng: numpy random generator.
    """
    def __init__(self, model, payoff, n_paths: int = 100_000,
                 n_steps: int = 50, seed: int = None):
        self.model = model
        self.payoff = payoff
        self.n_paths = n_paths
        self.n_steps = n_steps
        self.rng = None if seed is None else np.random.default_rng(seed)

    def price(self, S0: float, T: float, r: float) -> tuple:
        """
        Price the American option via Least-Squares Monte Carlo.

        Args:
            S0: Initial asset price.
            T: Time to maturity.
            r: Risk-free rate.

        Returns:
            (price, stderr): discounted price and its standard error estimate.
        """
        dt = T / self.n_steps
        paths = self.model.simulate(S0, T, self.n_paths, self.n_steps, rng=self.rng)
        n_paths, _ = paths.shape
        # initialize cashflows and exercise times at maturity
        cashflow = self.payoff(paths[:, -1])
        tau = np.full(n_paths, self.n_steps, dtype=int)

        disc = math.exp(-r * dt)
        # backward induction
        for t in range(self.n_steps - 1, 0, -1):
            St = paths[:, t]
            immediate = self.payoff(St)
            itm = immediate > 0
            if not np.any(itm):
                continue
            # discounted cashflows to time t
            Y = cashflow[itm] * (disc ** (tau[itm] - t))
            X = St[itm]
            # regress Y against basis [1, X, X^2]
            A = np.vstack([np.ones_like(X), X, X**2]).T
            coeffs, *_ = np.linalg.lstsq(A, Y, rcond=None)
            continuation = coeffs[0] + coeffs[1] * X + coeffs[2] * X**2
            exercise = immediate[itm] > continuation
            idx = np.where(itm)[0][exercise]
            cashflow[idx] = immediate[idx]
            tau[idx] = t

        # discount to time zero
        discounts = np.exp(-r * dt * tau)
        discounted = cashflow * discounts
        price = discounted.mean()
        stderr = discounted.std(ddof=1) / np.sqrt(self.n_paths)
        return price, stderr
