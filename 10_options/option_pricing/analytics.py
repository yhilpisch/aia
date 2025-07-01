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


def heston_price(S0, K, T, r, q, kappa, theta, xi, rho, v0, integration_limit=50):
    """
    Calculate the price of a European call option using the Heston model via characteristic function.
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
    - integration_limit: Upper bound for numerical integration to avoid overflow
    
    Returns:
    - call_price: Price of the European call option, floored at zero
    """
    def heston_char_func(u, S0, T, r, q, kappa, theta, xi, rho, v0, j):
        if j == 1:
            u_j = u - 0.5
            b_j = kappa + xi * rho
        else:
            u_j = u
            b_j = kappa
        x = np.log(S0)
        term1 = xi * rho * u_j * 1j - b_j
        term2 = xi**2 * (2 * u_j * 1j - u_j**2)
        d = np.sqrt(term1**2 - term2)
        g = (b_j - xi * rho * u_j * 1j + d) / (b_j - xi * rho * u_j * 1j - d)
        exp_dT = np.exp(np.clip(d * T, -700, 700))
        denom_log = 1 - g
        num_log = 1 - g * exp_dT
        if np.abs(denom_log) < 1e-10 or np.abs(num_log) < 1e-10:
            log_term = 0
        else:
            log_term = np.log(num_log / denom_log)
        term1_C = (b_j - xi * rho * u_j * 1j + d) * T
        term2_C = 2 * log_term
        C = (r - q) * u_j * 1j * T + (kappa * theta) / (xi**2) * (term1_C - term2_C)
        denom_D = 1 - g * exp_dT
        if np.abs(denom_D) < 1e-10:
            D = 0
        else:
            D = (b_j - xi * rho * u_j * 1j + d) / (xi**2) * (1 - exp_dT) / denom_D
        return np.exp(C + D * v0 + 1j * u_j * x)
    
    def integrand_P1(u):
        k = np.log(K)
        phi = heston_char_func(u - 1j, S0, T, r, q, kappa, theta, xi, rho, v0, 1)
        denom = 1j * u * heston_char_func(-1j, S0, T, r, q, kappa, theta, xi, rho, v0, 1)
        if np.abs(denom) < 1e-10:
            return 0
        return np.real(np.exp(-1j * u * k) * phi / denom)
    
    def integrand_P2(u):
        k = np.log(K)
        phi = heston_char_func(u, S0, T, r, q, kappa, theta, xi, rho, v0, 2)
        denom = 1j * u
        if np.abs(denom) < 1e-10:
            return 0
        return np.real(np.exp(-1j * u * k) * phi / denom)
    
    P1 = 0.5 + (1 / np.pi) * quad(integrand_P1, 0, integration_limit, limit=100)[0]
    P2 = 0.5 + (1 / np.pi) * quad(integrand_P2, 0, integration_limit, limit=100)[0]
    F = S0 * np.exp((r - q) * T)
    call_price = np.exp(-r * T) * (F * P1 - K * P2)
    return max(call_price, 0)  # Floor at zero to prevent negative prices


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
    xi = 0.02       # Volatility of variance
    rho = -0.7      # Correlation
    v0 = 0.04       # Initial variance
    
    # Calculate the call option price with a finite integration limit
    for K in [50, 75, 100, 125, 150]:
        call_price = heston_price(S0, K, T, r, q, kappa, theta, xi, rho, v0, integration_limit=50)
        print(f"European Call Option Price (Heston Model): {call_price:.4f}")

