import numpy as np
import math


class BSM:
    """
    Black-Scholes-Merton model for risk-neutral asset price simulation.

    Attributes:
        r (float): Risk-free interest rate.
        sigma (float): Volatility.
        q (float): Dividend yield.
    """
    def __init__(self, r: float, sigma: float, q: float = 0.0):
        self.r = r
        self.sigma = sigma
        self.q = q

    def simulate(self,
                 S0: float,
                 T: float,
                 n_paths: int,
                 n_steps: int = 1,
                 r: float = None,
                 q: float = None,
                 rng: np.random.Generator = None) -> np.ndarray:
        """
        Simulate asset price paths under the risk-neutral measure.

        Args:
            S0 (float): Initial asset price.
            T (float): Time to maturity.
            n_paths (int): Number of simulation paths.
            n_steps (int): Number of time steps per path.
            rng (np.random.Generator, optional): Random generator.

        Returns:
            np.ndarray: Simulated asset prices, shape (n_paths, n_steps+1).
        """
        if rng is None:
            rng = np.random.default_rng()
        if r is None:
            r = self.r
        if q is None:
            q = self.q

        dt = T / n_steps
        drift = (r - q - 0.5 * self.sigma ** 2) * dt
        diffusion = self.sigma * np.sqrt(dt)

        paths = np.empty((n_paths, n_steps + 1))
        paths[:, 0] = S0

        for t in range(1, n_steps + 1):
            z = rng.standard_normal(n_paths)
            paths[:, t] = paths[:, t - 1] * np.exp(drift + diffusion * z)

        return paths


# This class has been corrected by Gemini with regard to the discretization
# approach to yield better convergence and valuation results.
class Heston:
    """
    Heston stochastic volatility model.

    dS_t = (r - q) S_t dt + sqrt(v_t) S_t dW1
    dv_t = kappa*(theta - v_t) dt + xi*sqrt(max(v_t,0)) dW2
    corr(dW1, dW2) = rho

    Attributes:
        r (float): Risk-free rate.
        kappa (float): Mean reversion speed of variance.
        theta (float): Long-run variance.
        xi (float): Volatility of variance (vol-of-vol).
        rho (float): Correlation between asset and variance.
        v0 (float): Initial variance.
        q (float): Dividend yield.
    """
    def __init__(self,
                 r: float,
                 kappa: float,
                 theta: float,
                 xi: float,
                 rho: float,
                 v0: float,
                 q: float = 0.0):
        self.r = r
        self.kappa = kappa
        self.theta = theta
        self.xi = xi
        self.rho = rho
        self.v0 = v0
        self.q = q

    def simulate(self,
                 S0: float,
                 T: float,
                 n_paths: int,
                 n_steps: int = 50,
                 r: float = None,
                 q: float = None,
                 rng: np.random.Generator = None) -> np.ndarray:
        """
        Simulate asset price under Heston model via Euler full-truncation.

        Returns:
            np.ndarray: Asset paths shape (n_paths, n_steps+1).
        """
        if rng is None:
            rng = np.random.default_rng()
        if r is None:
            r = self.r
        if q is None:
            q = self.q

        # time increment
        dt = T / n_steps
        # initialize paths and variance
        S = np.full((n_paths, n_steps + 1), S0, dtype=float)
        v = np.full(n_paths, self.v0, dtype=float)

        for t in range(1, n_steps + 1):
            # draw correlated normals
            z1 = rng.standard_normal(n_paths)
            z2 = rng.standard_normal(n_paths)
            w1 = z1
            w2 = self.rho * z1 + math.sqrt(1 - self.rho ** 2) * z2

            # full truncation for variance
            v_pos = np.maximum(v, 0.0)

            # asset price update (Euler-log)
            drift = (r - q - 0.5 * v_pos) * dt
            diffusion = np.sqrt(v_pos * dt) * w1
            S[:, t] = S[:, t - 1] * np.exp(drift + diffusion)

            # variance update (full-truncation Euler)
            v = v + self.kappa * (self.theta - v) * dt + self.xi * np.sqrt(v_pos * dt) * w2
        return S


class MertonJumpDiffusion:
    """
    Merton jump-diffusion model for risk-neutral asset price simulation.

    dS/S = (r - q - lam * kappa - 0.5 * sigma**2) dt + sigma dW
           + (Y - 1) dN,    where log Y ~ N(mu_j, sigma_j**2), N~Poisson(lam dt)

    Attributes:
        r (float): Risk-free interest rate.
        sigma (float): Diffusion volatility.
        lam (float): Jump intensity (Poisson rate).
        mu_j (float): Mean of jump size log-normal distribution.
        sigma_j (float): Volatility of jump size log-normal distribution.
        q (float): Dividend yield.
    """
    def __init__(self,
                 r: float,
                 sigma: float,
                 lam: float,
                 mu_j: float,
                 sigma_j: float,
                 q: float = 0.0):
        self.r = r
        self.sigma = sigma
        self.lam = lam
        self.mu_j = mu_j
        self.sigma_j = sigma_j
        self.q = q
        # compensator to keep martingale: E[Y - 1]
        self.kappa = math.exp(mu_j + 0.5 * sigma_j ** 2) - 1

    def simulate(self,
                 S0: float,
                 T: float,
                 n_paths: int,
                 n_steps: int = 1,
                 r: float = None,
                 q: float = None,
                 rng=None) -> np.ndarray:
        """
        Simulate asset price paths under risk-neutral Merton jump-diffusion.

        Args:
            S0 (float): Initial asset price.
            T (float): Time to maturity.
            n_paths (int): Number of simulation paths.
            n_steps (int): Number of time steps per path.
            rng (np.random.Generator, optional): Random number generator.

        Returns:
            np.ndarray: Simulated asset prices, shape (n_paths, n_steps+1).
        """
        if rng is None:
            rng = np.random.default_rng()
        if r is None:
            r = self.r
        if q is None:
            q = self.q

        dt = T / n_steps
        drift = (r - q - self.lam * self.kappa - 0.5 * self.sigma ** 2) * dt
        diff_coeff = self.sigma * math.sqrt(dt)
        jump_mu = self.mu_j
        jump_sigma = self.sigma_j

        paths = np.empty((n_paths, n_steps + 1))
        paths[:, 0] = S0

        for t in range(1, n_steps + 1):
            # diffusion component
            z = rng.standard_normal(n_paths)
            # jumps: number of jumps ~ Poisson(lam dt)
            nj = rng.poisson(self.lam * dt, size=n_paths)
            # aggregate jump-size log-return: sum of nj iid normals
            # if nj=0, jump_log = 0
            jump_log = np.where(
                nj > 0,
                rng.normal(nj * jump_mu, np.sqrt(nj) * jump_sigma),
                0.0,
            )
            paths[:, t] = (
                paths[:, t - 1]
                * np.exp(drift + diff_coeff * z + jump_log)
            )
        return paths

class BCCModel:
    """
    Bates (Heston SV + Merton jumps) model Monte Carlo simulation with constant interest rate.

    S_t dynamics:
      dS/S = (r - q - lam*kappa_j - 0.5*v_t) dt + sqrt(v_t) dW1 + jumps
    v_t dynamics (Heston full truncation):
      dv = kappa*(theta - v_t) dt + xi*sqrt(max(v_t,0)) dW2

    Attributes:
        r (float): Constant risk-free rate.
        kappa (float): Mean-reversion speed of variance.
        theta (float): Long-run variance.
        xi (float): Volatility of variance.
        rho (float): Correlation between asset and variance processes.
        v0 (float): Initial variance.
        lam (float): Jump intensity.
        mu_j (float): Mean jump size (lognormal).
        sigma_j (float): Jump size volatility.
        q (float): Dividend yield.
    """
    def __init__(
        self,
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
    ):
        self.r = r
        self.kappa = kappa
        self.theta = theta
        self.xi = xi
        self.rho = rho
        self.v0 = v0
        self.lam = lam
        self.mu_j = mu_j
        self.sigma_j = sigma_j
        self.q = q
        # jump compensator E[e^J - 1]
        self.kappa_j = math.exp(mu_j + 0.5 * sigma_j ** 2) - 1

    def simulate(
        self,
        S0: float,
        T: float,
        n_paths: int,
        n_steps: int = 50,
        r: float = None,
        q: float = None,
        rng=None,
    ) -> np.ndarray:
        """
        Simulate asset price paths under the Bates model (Heston SV + Merton jumps).

        Returns:
            np.ndarray: Simulated asset prices, shape (n_paths, n_steps+1).
        """
        if rng is None:
            rng = np.random.default_rng()
        if r is None:
            r = self.r
        if q is None:
            q = self.q

        dt = T / n_steps
        S = np.empty((n_paths, n_steps + 1), dtype=float)
        v = np.empty(n_paths, dtype=float)
        S[:, 0] = S0
        v[:] = self.v0

        for t in range(1, n_steps + 1):
            # draw correlated normals for diffusion
            z1 = rng.standard_normal(n_paths)
            z2 = rng.standard_normal(n_paths)
            w1 = z1
            w2 = self.rho * z1 + math.sqrt(1 - self.rho ** 2) * z2

            # full truncation for variance
            v_pos_old = np.maximum(v, 0.0)

            # diffusion and jump for asset price using previous variance
            drift = (r - q - self.lam * self.kappa_j - 0.5 * v_pos_old) * dt
            diffusion = np.sqrt(v_pos_old * dt) * w1
            nj = rng.poisson(self.lam * dt, size=n_paths)
            jump_log = np.where(
                nj > 0,
                rng.normal(nj * self.mu_j, np.sqrt(nj) * self.sigma_j),
                0.0,
            )
            S[:, t] = S[:, t - 1] * np.exp(drift + diffusion + jump_log)

            # now update variance using Quadratic-Exponential (QE) scheme
            exp_k = math.exp(-self.kappa * dt)
            m = self.theta + (v - self.theta) * exp_k
            s2 = (
                v_pos_old * self.xi**2 * exp_k * (1 - exp_k) / self.kappa
                + self.theta * self.xi**2 / (2 * self.kappa) * (1 - exp_k)**2
            )
            psi = s2 / (m**2)
            v_new = np.empty_like(v)
            # threshold
            psi_c = 1.5
            mask1 = psi <= psi_c
            if np.any(mask1):
                psi1 = psi[mask1]
                m1 = m[mask1]
                b2 = 2 / psi1 - 1 + np.sqrt(2 / psi1) * np.sqrt(2 / psi1 - 1)
                a2 = m1 / (1 + b2)
                v_new[mask1] = a2 * (np.sqrt(b2) + w2[mask1])**2
            mask2 = ~mask1
            if np.any(mask2):
                psi2 = psi[mask2]
                m2 = m[mask2]
                p2 = (psi2 - 1) / (psi2 + 1)
                beta2 = (1 - p2) / m2
                U = rng.random(n_paths)[mask2]
                v2 = np.where(
                    U <= p2,
                    0.0,
                    -np.log((1 - U) / (1 - p2)) / beta2
                )
                v_new[mask2] = v2
            v = v_new

        return S