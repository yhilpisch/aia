#!/usr/bin/env python3
"""
black_scholes.py

Module implementing the Black-Scholes-Merton model for European option pricing.
"""
import math


class BlackScholes:
    """
    Class for pricing European call and put options using the Black-Scholes-Merton formula.
    """
    def __init__(self, S, K, T, r, sigma, q=0.0):
        """
        Initialize model parameters.

        Parameters:
        S     : float : current price of the underlying asset
        K     : float : strike price of the option
        T     : float : time to maturity in years
        r     : float : risk-free interest rate (annual)
        sigma : float : volatility of the underlying asset (annual)
        q     : float : continuous dividend yield (annual), default 0.0
        """
        self.S = float(S)
        self.K = float(K)
        self.T = float(T)
        self.r = float(r)
        self.sigma = float(sigma)
        self.q = float(q)

    @staticmethod
    def _norm_cdf(x):
        """
        Standard normal cumulative distribution function.
        """
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def _d1(self):
        return ((math.log(self.S / self.K)
                + (self.r - self.q + 0.5 * self.sigma ** 2) * self.T)
                / (self.sigma * math.sqrt(self.T)))

    def _d2(self):
        return self._d1() - self.sigma * math.sqrt(self.T)

    def call_price(self):
        """
        Compute the European call option price.
        """
        d1 = self._d1()
        d2 = self._d2()
        discounted_S = self.S * math.exp(-self.q * self.T)
        discounted_K = self.K * math.exp(-self.r * self.T)
        return discounted_S * self._norm_cdf(d1) - discounted_K * self._norm_cdf(d2)

    def put_price(self):
        """
        Compute the European put option price.
        """
        d1 = self._d1()
        d2 = self._d2()
        discounted_S = self.S * math.exp(-self.q * self.T)
        discounted_K = self.K * math.exp(-self.r * self.T)
        return discounted_K * self._norm_cdf(-d2) - discounted_S * self._norm_cdf(-d1)


if __name__ == '__main__':
    # Example usage
    params = {
        'S': 100,   # asset price
        'K': 100,   # strike price
        'T': 1,     # time to maturity (1 year)
        'r': 0.05,  # risk-free rate
        'sigma': 0.2,  # volatility
        'q': 0.0    # dividend yield
    }
    model = BlackScholes(**params)
    print(f"Call Price: {model.call_price():.4f}")
    print(f"Put  Price: {model.put_price():.4f}")
