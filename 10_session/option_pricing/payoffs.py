import numpy as np


class Payoff:
    """Base class for payoff definitions."""
    def __call__(self, S: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class CallPayoff(Payoff):
    """European call option payoff."""
    def __init__(self, strike: float):
        self.strike = strike

    def __call__(self, S: np.ndarray) -> np.ndarray:
        return np.maximum(S - self.strike, 0.0)


class PutPayoff(Payoff):
    """European put option payoff."""
    def __init__(self, strike: float):
        self.strike = strike

    def __call__(self, S: np.ndarray) -> np.ndarray:
        return np.maximum(self.strike - S, 0.0)