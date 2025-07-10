#!/usr/bin/env python3
"""
Benchmark Bates (1996) jump-diffusion with stochastic volatility European options
  (Heston+Merton jumps): MC vs semi-analytic via Lewis (2001)
"""

import os
import sys
import time
import argparse

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..')))
import numpy as np
from mcdxa.models import Bates
from mcdxa.payoffs import CallPayoff, PutPayoff
from mcdxa.pricers.european import EuropeanPricer
from mcdxa.analytics import bates_price


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Bates model European options: MC vs semi-analytic"
    )
    parser.add_argument("--K", type=float, default=100.0, help="Strike price")
    parser.add_argument("--T", type=float, default=1.0, help="Time to maturity")
    parser.add_argument("--r", type=float, default=0.05, help="Risk-free rate")
    parser.add_argument("--kappa", type=float, default=2.0, help="Heston mean-reversion speed kappa")
    parser.add_argument("--theta", type=float, default=0.04, help="Heston long-term variance theta")
    parser.add_argument("--xi", type=float, default=0.2, help="Heston vol-of-vol xi")
    parser.add_argument("--rho", type=float, default=-0.7, help="Heston correlation rho")
    parser.add_argument("--v0", type=float, default=0.02, help="Heston initial variance v0")
    parser.add_argument("--lam", type=float, default=0.3, help="Jump intensity lambda")
    parser.add_argument("--mu_j", type=float, default=-0.1, help="Jump mean mu_j")
    parser.add_argument("--sigma_j", type=float, default=0.2, help="Jump volatility sigma_j")
    parser.add_argument("--n_paths", type=int, default=100000, help="Number of Monte Carlo paths")
    parser.add_argument("--n_steps", type=int, default=50, help="Number of time steps per path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--q", type=float, default=0.0, help="Dividend yield")
    args = parser.parse_args()

    model = Bates(
        args.r, args.kappa, args.theta, args.xi, args.rho,
        args.v0, args.lam, args.mu_j, args.sigma_j, q=args.q
    )
    moneyness = 0.10
    scenarios = []
    for opt_type, payoff_cls in [("call", CallPayoff), ("put", PutPayoff)]:
        if opt_type == "call":
            S0_cases = [args.K * (1 + moneyness), args.K, args.K * (1 - moneyness)]
        else:
            S0_cases = [args.K * (1 - moneyness), args.K, args.K * (1 + moneyness)]
        for case, S0_case in zip(["ITM", "ATM", "OTM"], S0_cases):
            scenarios.append((opt_type, payoff_cls, case, S0_case))

    header = f"{'Type':<6}{'Case':<6}{'MC Price':>12}{'StdErr':>12}{'Analytic':>12}{'Abs Err':>12}{'% Err':>10}{'Time(s)':>12}"
    print(header)
    print('-' * len(header))

    for opt_type, payoff_cls, case, S0_case in scenarios:
        payoff = payoff_cls(args.K)
        pricer = EuropeanPricer(
            model, payoff, n_paths=args.n_paths, n_steps=args.n_steps, seed=args.seed
        )
        t0 = time.time()
        price_mc, stderr = pricer.price(S0_case, args.T, args.r)
        dt = time.time() - t0

        price_an = bates_price(
            S0_case, args.K, args.T, args.r,
            args.kappa, args.theta, args.xi, args.rho, args.v0,
            args.lam, args.mu_j, args.sigma_j,
            q=args.q, option_type=opt_type
        )

        abs_err = abs(price_mc - price_an)
        pct_err = abs_err / price_an * 100.0 if price_an != 0 else float('nan')
        print(f"{opt_type.capitalize():<6}{case:<6}{price_mc:12.6f}{stderr:12.6f}{price_an:12.6f}{abs_err:12.6f}{pct_err:10.2f}{dt:12.4f}")


if __name__ == "__main__":
    main()
