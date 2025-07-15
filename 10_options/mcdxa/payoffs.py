import numpy as np


class Payoff:
    """Base class for payoff definitions."""
    def __call__(self, S: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class CustomPayoff(Payoff):
    """
    Custom payoff defined by an arbitrary function of the terminal asset price.

    Args:
        func (callable): Function mapping terminal price array (n_paths,)
            or scalar to payoff values. The function should accept a numpy
            array or scalar and return an array or scalar of payoffs.

    Example:
        # payoff = max(sqrt(S_T) - K, 0)
        payoff = CustomPayoff(lambda s: np.maximum(np.sqrt(s) - K, 0))
    """
    def __init__(self, func):
        if not callable(func):
            raise TypeError(f"func must be callable, got {type(func)}")
        self.func = func

    def __call__(self, S: np.ndarray) -> np.ndarray:
        S = np.asarray(S)
        # extract terminal price if full path provided
        S_end = S[:, -1] if S.ndim == 2 else S
        # apply custom function to terminal prices
        return np.asarray(self.func(S_end))


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
