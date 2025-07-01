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
        S = np.asarray(S)
        # handle terminal price if full path provided
        S_end = S[:, -1] if S.ndim == 2 else S
        return np.maximum(S_end - self.strike, 0.0)


class PutPayoff(Payoff):
    """European put option payoff."""
    def __init__(self, strike: float):
        self.strike = strike

    def __call__(self, S: np.ndarray) -> np.ndarray:
        S = np.asarray(S)
        S_end = S[:, -1] if S.ndim == 2 else S
        return np.maximum(self.strike - S_end, 0.0)


class AsianCallPayoff(Payoff):
    """Arithmetic Asian (path-dependent) European call payoff."""
    def __init__(self, strike: float):
        self.strike = strike

    def __call__(self, S: np.ndarray) -> np.ndarray:
        S = np.asarray(S)
        # average price over the path
        avg = S.mean(axis=1) if S.ndim == 2 else S
        return np.maximum(avg - self.strike, 0.0)


class AsianPutPayoff(Payoff):
    """Arithmetic Asian (path-dependent) European put payoff."""
    def __init__(self, strike: float):
        self.strike = strike

    def __call__(self, S: np.ndarray) -> np.ndarray:
        S = np.asarray(S)
        avg = S.mean(axis=1) if S.ndim == 2 else S
        return np.maximum(self.strike - avg, 0.0)


class LookbackCallPayoff(Payoff):
    """Lookback (path-dependent) European call payoff (max(S) - strike)."""
    def __init__(self, strike: float):
        self.strike = strike

    def __call__(self, S: np.ndarray) -> np.ndarray:
        S = np.asarray(S)
        high = S.max(axis=1) if S.ndim == 2 else S
        return np.maximum(high - self.strike, 0.0)


class LookbackPutPayoff(Payoff):
    """Lookback (path-dependent) European put payoff (strike - min(S))."""
    def __init__(self, strike: float):
        self.strike = strike

    def __call__(self, S: np.ndarray) -> np.ndarray:
        S = np.asarray(S)
        low = S.min(axis=1) if S.ndim == 2 else S
        return np.maximum(self.strike - low, 0.0)