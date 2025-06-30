import numpy as np


def discount_factor(r: float, T: float) -> float:
    """Compute discount factor exp(-r*T)."""
    return np.exp(-r * T)