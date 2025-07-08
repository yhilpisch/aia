# Test Suite Highlights

This document summarizes the comprehensive pytest-based test suite for the option_pricing package, following the project outline.

```
tests/
├── conftest.py               # test fixtures (fixed RNG seed)
├── test_models.py            # model simulation unit tests (BSM, Heston, MJD)
├── test_payoffs.py           # payoff function tests (vanilla & path-dependent)
├── test_monte_carlo.py       # core Monte Carlo engine tests
├── test_pricers_european.py  # EuropeanPricer vs analytic BSM benchmarks
└── test_pricers_american.py  # American pricers (LSM MC vs CRR binomial)
```

**Key test scenarios:**

- **Fixed RNG seed** via `conftest.py` for reproducible MC results.
- **BSM zero-volatility**: exact deterministic growth of paths.
- **Heston simulation**: non-negative paths of correct shape under Euler truncation.
- **Merton jump-diffusion**: pure jump tests with zero jump size variance.
- **Vanilla payoffs**: call/put payoffs on sample spot arrays.
- **Path-dependent payoffs**: arithmetic Asian & lookback payoffs on synthetic paths.
- **Monte Carlo engine**: zero-volatility, in-the-money call to verify price & stderr.
- **EuropeanPricer**: matches analytic BSM price when volatility = 0.
- **American pricers**:
  - CRR binomial call with no volatility → immediate exercise intrinsic value.
  - Longstaff-Schwartz put with no volatility → immediate exercise intrinsic value, zero stderr.

**Running the tests:**

```bash
pytest -q
```
