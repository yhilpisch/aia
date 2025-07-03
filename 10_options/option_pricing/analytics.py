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
    Analytical Black-Scholes-Merton price for European call or put.

    Args:
        S0: Spot price
        K: Strike price
        T: Time to maturity
        r: Risk-free rate
        sigma: Volatility
        q: Dividend yield
        option_type: 'call' or 'put'
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
    n_terms: int = 50,
) -> float:
    """
    Analytical Merton jump-diffusion European call price via Poisson-series expansion.

    Uses the infinite sum: sum_{n=0..n_terms} e^{-lam*T}(lam*T)^n/n! * BS_call_n,
    where BS_call_n uses adjusted drift and volatility:
        r_n = r - lam*(exp(mu_j+0.5*sigma_j^2)-1) + n*mu_j/T
        sigma_n = sqrt(sigma^2 + n*sigma_j^2/T)
    """
    kappa = math.exp(mu_j + 0.5 * sigma_j ** 2) - 1
    lamT = lam * T
    price = 0.0
    for n in range(n_terms + 1):
        p_n = math.exp(-lamT) * lamT ** n / math.factorial(n)
        sigma_n = math.sqrt(sigma * sigma + n * sigma_j * sigma_j / T)
        r_n = r - lam * kappa + n * mu_j / T
        sqrtT = math.sqrt(T)
        d1 = (math.log(S0 / K) + (r_n - q + 0.5 * sigma_n ** 2) * T) / (sigma_n * sqrtT)
        d2 = d1 - sigma_n * sqrtT
        call_n = (
            S0 * math.exp(-q * T) * norm_cdf(d1)
            - K * math.exp(-r * T) * norm_cdf(d2)
        )
        price += p_n * call_n
    return price


# the following Heston pricing implementation is from Gemini, after numerous tries with
# different LLMs, basically none was able to provide a properly working implementation
# Gemini only came up with that one after having seen my own reference implementation
# from my book "Derivatives Analytics with Python"; basically the firs time that
# none of the AI Assistants was able to provide a solution to such a quant finance problem
def heston_price(S0, K, T, r, q, kappa, theta, xi, rho, v0, option_type="call", integration_limit=250):
    """
    Calculate the price of a European call option using the Heston model via the single-integral Lewis (2001) formula.
    Includes a fix to prevent negative prices by flooring at zero.
    
    Parameters:
    - S0: Initial stock price
    - K: Strike price
    - T: Time to maturity (in years)
    - r: Risk-free interest rate
    - q: Dividend yield
    - kappa: Mean reversion rate of variance
    - theta: Long-term variance
    - xi: Volatility of variance (vol of vol)
    - rho: Correlation between stock price and variance processes
    - v0: Initial variance
    - option_type: 'call' or 'put'
    - integration_limit: Upper bound for numerical integration
    
    Returns:
    - call_price: Price of the European call option, floored at zero
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

