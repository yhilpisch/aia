import numpy as np
import math
from scipy.integrate import quad
from .models import Bates


def simulate_bates(
    S0: float,
    T: float,
    r: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    v0: float,
    lam: float,
    mu_j: float,
    sigma_j: float,
    q: float = 0.0,
    n_paths: int = 10000,
    n_steps: int = 50,
    rng: np.random.Generator = None,
) -> np.ndarray:
    """
    Wrapper: instantiate Bates model and simulate via its .simulate() method.
    """
    model = Bates(r, kappa, theta, xi, rho, v0, lam, mu_j, sigma_j, q)
    return model.simulate(S0, T, n_paths, n_steps, rng=rng)


def bates_price(
    S0: float,
    K: float,
    T: float,
    r: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    v0: float,
    lam: float,
    mu_j: float,
    sigma_j: float,
    q: float = 0.0,
    option_type: str = "call",
    integration_limit: float = 250,
) -> float:
    """
    Bates (1996) model price for European call or put via Lewis (2001) single-integral.

    Combines Heston stochastic volatility characteristic function
    with log-normal jumps (Merton).
    """
    def _char_heston(u):
        d = np.sqrt((kappa - rho * xi * u * 1j) ** 2 + (u ** 2 + u * 1j) * xi ** 2)
        g = (kappa - rho * xi * u * 1j - d) / (kappa - rho * xi * u * 1j + d)
        # add jump drift compensator E[Y - 1]
        kappa_j = math.exp(mu_j + 0.5 * sigma_j ** 2) - 1
        C = (
            (r - q - lam * kappa_j) * u * 1j * T
            + (kappa * theta / xi ** 2)
            * ((kappa - rho * xi * u * 1j - d) * T
               - 2 * np.log((1 - g * np.exp(-d * T)) / (1 - g)))
        )
        D = ((kappa - rho * xi * u * 1j - d) / xi ** 2) * \
            ((1 - np.exp(-d * T)) / (1 - g * np.exp(-d * T)))
        return np.exp(C + D * v0)

    def _char_bates(u):
        # add jump component to characteristic function
        jump_cf = np.exp(lam * T * (np.exp(1j * u * mu_j - 0.5 * u ** 2 * sigma_j ** 2) - 1))
        return _char_heston(u) * jump_cf

    def _lewis_integrand(u):
        cf_val = _char_bates(u - 0.5j)
        return (np.exp(1j * u * math.log(S0 / K)) * cf_val).real / (u ** 2 + 0.25)

    integral_value = quad(_lewis_integrand, 0, integration_limit)[0]
    call_price = S0 * math.exp(-q * T) - math.exp(-r * T) * math.sqrt(S0 * K) / math.pi * integral_value
    if option_type == "call":
        price = call_price
    elif option_type == "put":
        price = call_price - S0 * math.exp(-q * T) + K * math.exp(-r * T)
    else:
        raise ValueError("Option type must be 'call' or 'put'.")
    return max(price, 0.0)
