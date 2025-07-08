import numpy as np
from scipy.integrate import quad
import math


def norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))


def bsm_price(
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    q: float = 0.0,
    option_type: str = "call",
) -> float:
    """
    Black-Scholes-Merton (BSM) price for European call or put option.

    Parameters:
    - S0: Spot price
    - K: Strike price
    - T: Time to maturity (in years)
    - r: Risk-free interest rate
    - sigma: Volatility of the underlying asset
    - q: Dividend yield
    - option_type: 'call' or 'put'

    Returns:
    - price: Option price (call or put)
    """
    # handle zero volatility (degenerate case)
    if sigma <= 0 or T <= 0:
        # forward intrinsic value, floored at zero
        forward = S0 * math.exp(-q * T) - K * math.exp(-r * T)
        if option_type == "call":
            return max(forward, 0.0)
        else:
            return max(-forward, 0.0)

    d1 = (math.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / \
        (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == "call":
        return S0 * math.exp(-q * T) * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    elif option_type == "put":
        return K * math.exp(-r * T) * norm_cdf(-d2) - S0 * math.exp(-q * T) * norm_cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")


def merton_price(
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    lam: float = 0.0,
    mu_j: float = 0.0,
    sigma_j: float = 0.0,
    q: float = 0.0,
    option_type: str = "call",
    integration_limit: float = 250,
) -> float:
    """
    European option price under the Merton (1976) jump-diffusion model via Lewis (2001)
    single-integral formula.

    Parameters:
    - S0: Initial stock price
    - K: Strike price
    - T: Time to maturity (in years)
    - r: Risk-free interest rate
    - sigma: Volatility of the diffusion component
    - lam: Jump intensity (lambda)
    - mu_j: Mean of log jump size
    - sigma_j: Standard deviation of log jump size
    - q: Dividend yield
    - option_type: 'call' or 'put'
    - integration_limit: Upper bound for numerical integration

    Returns:
    - price: Price of the European option (call or put)
    """
    def _char(u):
        # Jump-diffusion characteristic function of log-returns under risk-neutral measure
        kappa_j = math.exp(mu_j + 0.5 * sigma_j ** 2) - 1
        drift = r - q - lam * kappa_j - 0.5 * sigma ** 2
        return np.exp(
            (1j * u * drift - 0.5 * u ** 2 * sigma ** 2) * T
            + lam * T * (np.exp(1j * u * mu_j - 0.5 *
                                u ** 2 * sigma_j ** 2) - 1)
        )

    def _lewis_integrand(u):
        # Lewis (2001) integrand for call under jump-diffusion
        cf_val = _char(u - 0.5j)
        return 1.0 / (u ** 2 + 0.25) * (np.exp(1j * u * math.log(S0 / K)) * cf_val).real

    integral_value = quad(_lewis_integrand, 0, integration_limit)[0]
    call_price = S0 * np.exp(-q * T) - np.exp(-r * T) * \
        np.sqrt(S0 * K) / np.pi * integral_value

    if option_type == "call":
        price = call_price
    elif option_type == "put":
        price = call_price - S0 * math.exp(-q * T) + K * math.exp(-r * T)
    else:
        raise ValueError("Option type must be 'call' or 'put'.")

    return max(price, 0.0)


# the following Heston pricing implementation is from Gemini, after numerous tries with
# different LLMs, basically none was able to provide a properly working implementation;
# Gemini only came up with that one after having seen my own reference implementation
# from my book "Derivatives Analytics with Python"; basically the first time that
# none of the AI Assistants was able to provide a solution to such a quant finance problem


def heston_price(
    S0: float,
    K: float,
    T: float,
    r: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    v0: float,
    q: float = 0.0,
    option_type: str = "call",
    integration_limit: float = 250,
) -> float:
    """
    Heston (1993) model price for European call or put option via Lewis (2001)
    single-integral formula. Negative prices are floored at zero.

    Parameters:
    - S0: Initial stock price
    - K: Strike price
    - T: Time to maturity (in years)
    - r: Risk-free interest rate
    - kappa: Mean reversion rate of variance
    - theta: Long-term variance
    - xi: Volatility of variance (vol of vol)
    - rho: Correlation between stock price and variance processes
    - v0: Initial variance
    - q: Dividend yield
    - option_type: 'call' or 'put'
    - integration_limit: Upper bound for numerical integration

    Returns:
    - price: Price of the European option (call or put)
    """

    def _lewis_integrand(u, S0, K, T, r, q, kappa, theta, xi, rho, v0):
        """The integrand for the Lewis (2001) single-integral formula."""

        # Calculate the characteristic function value at the complex point u - i/2
        char_func_val = _lewis_char_func(
            u - 0.5j, T, r, q, kappa, theta, xi, rho, v0)

        # The Lewis formula integrand
        integrand = 1 / (u**2 + 0.25) * \
            (np.exp(1j * u * np.log(S0 / K)) * char_func_val).real

        return integrand

    def _lewis_char_func(u, T, r, q, kappa, theta, xi, rho, v0):
        """The Heston characteristic function of the log-price."""

        d = np.sqrt((kappa - rho * xi * u * 1j)**2 + (u**2 + u * 1j) * xi**2)

        g = (kappa - rho * xi * u * 1j - d) / (kappa - rho * xi * u * 1j + d)

        C = (r - q) * u * 1j * T + (kappa * theta / xi**2) * (
            (kappa - rho * xi * u * 1j - d) * T - 2 *
            np.log((1 - g * np.exp(-d * T)) / (1 - g))
        )

        D = ((kappa - rho * xi * u * 1j - d) / xi**2) * \
            ((1 - np.exp(-d * T)) / (1 - g * np.exp(-d * T)))

        return np.exp(C + D * v0)

    # Perform the integration
    integral_value = quad(
        lambda u: _lewis_integrand(
            u, S0, K, T, r, q, kappa, theta, xi, rho, v0),
        0,
        integration_limit
    )[0]

    # Calculate the final call price using the Lewis formula
    call_price = S0 * np.exp(-q * T) - np.exp(-r * T) * \
        np.sqrt(S0 * K) / np.pi * integral_value

    if option_type == "call":
        price = call_price
    elif option_type == "put":
        price = call_price - S0 * math.exp(-q * T) + K * math.exp(-r * T)
    else:
        raise ValueError("Option type must be 'call' or 'put'.")

    return max(price, 0.0)


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
