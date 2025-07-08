import os
import sys
import pytest

# allow tests to import the top-level package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(autouse=True)
def fixed_seed(monkeypatch):
    """Fix the RNG seed for reproducible Monte Carlo tests."""
    import numpy as np
    rng = np.random.default_rng(12345)
    monkeypatch.setattr(np.random, 'default_rng', lambda *args, **kwargs: rng)
    yield
