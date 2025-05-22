"""
bsm_codex.py
Black-Scholes-Merton option pricing formula implementation for European calls and puts.
"""
import math
import unittest

class BlackScholesMerton:
    """
    Black-Scholes-Merton model for European option pricing.

    Attributes:
        S (float): Current price of the underlying asset.
        K (float): Strike price of the option.
        T (float): Time to maturity in years.
        r (float): Risk-free interest rate (annualized, continuous compounding).
        sigma (float): Volatility of the underlying asset (annualized).
        q (float): Dividend yield of the underlying asset (annualized, continuous compounding).
    """

    def __init__(self, S, K, T, r, sigma, q=0.0):
        self.S = float(S)
        self.K = float(K)
        self.T = float(T)
        self.r = float(r)
        self.sigma = float(sigma)
        self.q = float(q)

    @staticmethod
    def _cdf(x):
        """
        Standard normal cumulative distribution function.
        """
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def _d1(self):
        """
        Calculate d1 in the BSM formula.
        """
        return (
            math.log(self.S / self.K)
            + (self.r - self.q + 0.5 * self.sigma ** 2) * self.T
        ) / (self.sigma * math.sqrt(self.T))

    def _d2(self):
        """
        Calculate d2 in the BSM formula.
        """
        return self._d1() - self.sigma * math.sqrt(self.T)

    def call_price(self):
        """
        Calculate the European call option price.

        Returns:
            float: Call option price.
        """
        d1 = self._d1()
        d2 = self._d2()
        return (
            self.S * math.exp(-self.q * self.T) * self._cdf(d1)
            - self.K * math.exp(-self.r * self.T) * self._cdf(d2)
        )

    def put_price(self):
        """
        Calculate the European put option price.

        Returns:
            float: Put option price.
        """
        d1 = self._d1()
        d2 = self._d2()
        return (
            self.K * math.exp(-self.r * self.T) * self._cdf(-d2)
            - self.S * math.exp(-self.q * self.T) * self._cdf(-d1)
        )


class TestBlackScholesMerton(unittest.TestCase):
    """Unit tests for BlackScholesMerton model."""

    def test_call_price(self):
        bsm = BlackScholesMerton(S=100, K=100, T=1, r=0.05, sigma=0.2)
        price = bsm.call_price()
        # Known value ~10.4506
        self.assertAlmostEqual(price, 10.4506, places=4)

    def test_put_price(self):
        bsm = BlackScholesMerton(S=100, K=100, T=1, r=0.05, sigma=0.2)
        price = bsm.put_price()
        # Known value ~5.5735
        self.assertAlmostEqual(price, 5.5735, places=4)

    def test_put_call_parity(self):
        bsm = BlackScholesMerton(S=50, K=55, T=0.5, r=0.03, sigma=0.25, q=0.01)
        call = bsm.call_price()
        put = bsm.put_price()
        # Call - Put should equal forward price difference
        lhs = call - put
        rhs = bsm.S * math.exp(-bsm.q * bsm.T) - bsm.K * math.exp(-bsm.r * bsm.T)
        self.assertAlmostEqual(lhs, rhs, places=8)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()