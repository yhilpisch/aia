import numpy as np
import pytest

@pytest.fixture
def rng():
    """Random number generator with fixed seed for reproducibility."""
    return np.random.default_rng(42)