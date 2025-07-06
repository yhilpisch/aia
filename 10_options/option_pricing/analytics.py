import numpy as np
from scipy.integrate import quad
import math


def norm_cdf(x: float) -> float:
    """
    Standard normal cumulative distribution function.

    Args:
        x (float): Value at which to evaluate the CDF.

    Returns:
        float: Cumulative distribution function of a standard normal at x.
    """
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
    Analytical Black-Scholes-Merton price for a European option.

    Args:
        S0 (float): Initial asset price.
        K (float): Strike price.
        T (float): Time to maturity.
        r (float): Risk-free interest rate.
        sigma (float): Volatility of the underlying.
        q (float): Dividend yield. Default is 0.0.
        option_type (str): 'call' or 'put'. Default is 'call'.

    Returns:
        float: Black-Scholes-Merton option price.
    """
    d1 = (math.log(S0 / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
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
    lam: float,
    mu_j: float,
    sigma_j: float,
    q: float = 0.0,
    option_type: str = "call",
    n_terms: int = None,
) -> float:
    """
    European option price (call or put) under the Merton jump-diffusion model
    via the Lewis (2001) characteristic function single-integral formula.

    Args:
        S0 (float): Initial asset price.
        K (float): Strike price.
        T (float): Time to maturity.
        r (float): Risk-free interest rate.
        sigma (float): Diffusion volatility.
        lam (float): Jump intensity (Poisson rate).
        mu_j (float): Mean of log-jump size.
        sigma_j (float): Volatility of log-jump size.
        q (float): Dividend yield.
        option_type (str): 'call' or 'put'. Default is 'call'.
        n_terms (int, optional): Retained for compatibility (not used by CF method).

    Returns:
        float: European option price (floored at zero).
    """
    # Jump compensator: E[e^{Xi} - 1]
    kappa = math.exp(mu_j + 0.5 * sigma_j ** 2) - 1

    # Characteristic function of log-return X = ln(S_T/S0)
    def phi(u):
        omega = r - q - 0.5 * sigma * sigma - lam * kappa
        return np.exp(
            1j * u * omega * T
            - 0.5 * sigma * sigma * u * u * T
            + lam * T * (np.exp(1j * u * mu_j - 0.5 * sigma_j * sigma_j * u * u) - 1)
        )

    # Integrand for Lewis formula
    def integrand(u):
        a = u - 0.5j
        phi_val = phi(a)
        x = math.log(S0 / K)
        return (np.exp(1j * u * x) * phi_val).real / (u * u + 0.25)

    # Numerical integration over [0, ∞)
    integral_value = quad(integrand, 0.0, np.inf, limit=1000)[0]

    # Compute call price
    call_price = (
        S0 * math.exp(-q * T)
        - (math.exp(-r * T) * math.sqrt(S0 * K) / math.pi) * integral_value
    )
    # Floor at zero
    call_price = max(call_price, 0.0)
    if option_type == "call":
        return call_price
    elif option_type == "put":
        # Put-call parity: P = C - S0*e^{-qT} + K*e^{-rT}
        put_price = call_price - S0 * math.exp(-q * T) + K * math.exp(-r * T)
        return max(put_price, 0.0)
    else:
        raise ValueError("option_type must be 'call' or 'put'")


# the following Heston pricing implementation is from Gemini, after numerous tries with
# different LLMs, basically none was able to provide a properly working implementation
# Gemini only came up with that one after having seen my own reference implementation
# from my book "Derivatives Analytics with Python"; basically the firs time that
# none of the AI Assistants was able to provide a solution to such a quant finance problem
def heston_price(
    S0: float,
    K: float,
    T: float,
    r: float,
    q: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    v0: float,
    option_type: str = "call",
    integration_limit: float = 250.0,
) -> float:
    """
    European option price under the Heston stochastic volatility model via the Lewis (2001)
    single-integral characteristic function formula.

    Args:
        S0 (float): Initial asset price.
        K (float): Strike price.
        T (float): Time to maturity.
        r (float): Risk-free interest rate.
        q (float): Dividend yield.
        kappa (float): Mean-reversion speed of variance.
        theta (float): Long-run variance of variance process.
        xi (float): Volatility of variance (vol-of-vol).
        rho (float): Correlation between asset price and variance.
        v0 (float): Initial variance.
        option_type (str): 'call' or 'put'.
        integration_limit (float): Upper limit for numerical integration.

    Returns:
        float: European option price (call or put), floored at zero.
    """
    
    
    def _lewis_integrand(u, S0, K, T, r, q, kappa, theta, xi, rho, v0):
        """The integrand for the Lewis (2001) single-integral formula."""

        # Calculate the characteristic function value at the complex point u - i/2
        char_func_val = _lewis_char_func(u - 0.5j, T, r, q, kappa, theta, xi, rho, v0)

        # The Lewis formula integrand
        integrand = 1 / (u**2 + 0.25) * (np.exp(1j * u * np.log(S0 / K)) * char_func_val).real

        return integrand


    def _lewis_char_func(u, T, r, q, kappa, theta, xi, rho, v0):
        """The Heston characteristic function of the log-price."""
        
        d = np.sqrt((kappa - rho * xi * u * 1j)**2 + (u**2 + u * 1j) * xi**2)
        
        g = (kappa - rho * xi * u * 1j - d) / (kappa - rho * xi * u * 1j + d)
        
        C = (r - q) * u * 1j * T + (kappa * theta / xi**2) * (
            (kappa - rho * xi * u * 1j - d) * T - 2 * np.log((1 - g * np.exp(-d * T)) / (1 - g))
        )
        
        D = ((kappa - rho * xi * u * 1j - d) / xi**2) * ((1 - np.exp(-d * T)) / (1 - g * np.exp(-d * T)))
        
        return np.exp(C + D * v0)
    
    # Perform the integration
    integral_value = quad(
        lambda u: _lewis_integrand(u, S0, K, T, r, q, kappa, theta, xi, rho, v0),
        0, 
        integration_limit
    )[0]

    # Calculate the final call price using the Lewis formula
    call_price = S0 * np.exp(-q * T) - np.exp(-r * T) * np.sqrt(S0 * K) / np.pi * integral_value
    
    if option_type == "call":
        return max(0, call_price)
    elif option_type == "put":
        return max(0, call_price - S0 * math.exp(-q * T) + K * math.exp(-r * T))
    else:
        raise ValueError("Option type must be 'call' or 'put'.")


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
        call_price = heston_price(S0, K, T, r, q, kappa, theta, xi, rho, v0, integration_limit=50)
        print(f"European Call Option Price (Heston Model): {call_price:.4f}")

