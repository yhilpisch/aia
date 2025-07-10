import numpy as np
from scipy.integrate import quad
import math

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
