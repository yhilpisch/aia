import numpy as np
from scipy.integrate import quad
import math

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
