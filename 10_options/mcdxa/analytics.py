# core pricing functions
from .bsm     import norm_cdf, bsm_price
from .merton  import merton_price
from .heston  import heston_price
from .bates   import simulate_bates, bates_price

# Test script with provided parameters
if __name__ == "__main__":
    # Model parameters
    S0 = 100.0      # Initial stock price
    K = 100.0       # Strike price
    T = 1.0         # Time to maturity (1 year)
    r = 0.05        # Risk-free rate
    q = 0.0         # Dividend yield
    kappa = 2.0     # Mean reversion rate
    theta = 0.04    # Long-term variance
    xi = 0.2        # Volatility of variance
    rho = -0.7      # Correlation
    v0 = 0.02       # Initial variance

    # Calculate the call option price with a finite integration limit
    for K in [50, 75, 100, 125, 150]:
        call_price = heston_price(
            S0, K, T, r,
            kappa, theta, xi, rho, v0,
            q=q,
            integration_limit=50
        )
        print(f"European Call Option Price (Heston Model): {call_price:.4f}")
