# mcdxa

![The Python Quants GmbH Logo](https://hilpisch.com/tpq_logo.png)

mcdxa is a Python package for pricing European and American options with arbitrary payoffs via Monte Carlo simulation and analytic models. It provides a modular framework that cleanly separates stochastic asset price models, payoff definitions (including plain‑vanilla, path‑dependent, and custom functions), Monte Carlo engines, and pricer classes for European and American-style options.

## Features

- **Stochastic models**: Black–Scholes–Merton (GBM), Merton jump‑diffusion (Merton), Heston stochastic volatility, and Bates (Heston + Merton jumps).
- **Payoffs**: vanilla calls/puts, arithmetic Asian, lookback, and fully custom payoff functions via `CustomPayoff`.
- **Monte Carlo engine**: generic path generator and pricing framework with standard error estimation.
- **European pricer**: Monte Carlo wrapper with direct comparison to Black–Scholes analytic formulas.
- **American pricers**: Cox‑Ross‑Rubinstein binomial tree and Longstaff‑Schwartz least-squares Monte Carlo.
- **Analytics**: built‑in functions for Black–Scholes and Merton jump‑diffusion analytic pricing.

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/yhilpisch/mcdxa.git
cd mcdxa
pip install -e .
```

## Quickstart

```python
import numpy as np
from mcdxa.models import BSM
from mcdxa.payoffs import CallPayoff
from mcdxa.pricers.european import EuropeanPricer
from mcdxa.analytics import bsm_price

# Parameters
S0, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.2

# Define model and payoff
model = BSM(r, sigma)
payoff = CallPayoff(K)

# Monte Carlo pricing
pricer = EuropeanPricer(model, payoff, n_paths=50_000, n_steps=50, seed=42)
price_mc, stderr = pricer.price(S0, T, r)

# Analytic Black–Scholes price for comparison
price_bs = bsm_price(S0, K, T, r, sigma, option_type='call')

print(f"MC Price: {price_mc:.4f} ± {stderr:.4f}")
print(f"BS Price: {price_bs:.4f}")
```

## Documentation and Examples

Explore the [Jupyter notebook tutorial](scripts/mcdxa.ipynb) for detailed examples on custom payoffs, path simulations, convergence plots, and American option pricing.

## Testing

Run the full test suite with pytest:

```bash
pytest -q
```

## Company

**The Python Quants GmbH**

© 2025 The Python Quants GmbH. All rights reserved.
