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
