#!/usr/bin/env python
"""
Benchmark path-dependent European payoffs (Asian, Lookback) under BSM Monte Carlo.
Shows ATM/ITM/OTM results for calls and puts.
"""

import os
import sys
import time
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import numpy as np

from mcdxa.models import BSM
from mcdxa.payoffs import (
    AsianCallPayoff, AsianPutPayoff,
    LookbackCallPayoff, LookbackPutPayoff
)
from mcdxa.pricers.european import EuropeanPricer


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark path-dependent European payoffs under BSM Monte Carlo"
    )
    parser.add_argument("--K", type=float, default=100.0, help="Strike price")
    parser.add_argument("--T", type=float, default=1.0, help="Time to maturity")
    parser.add_argument("--r", type=float, default=0.05, help="Risk-free rate")
    parser.add_argument("--sigma", type=float, default=0.2, help="Volatility")
    parser.add_argument("--n_paths", type=int, default=100_000,
                        help="Number of Monte Carlo paths")
    parser.add_argument("--n_steps", type=int, default=50,
                        help="Number of time steps per path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    # Base BSM model
    model = BSM(args.r, args.sigma)

    # Scenarios: ATM, ITM, OTM (varying S0, fixed K)
    moneyness = 0.10
    scenarios = [
        ("ATM", args.K),
        ("ITM", args.K * (1 + moneyness)),
        ("OTM", args.K * (1 - moneyness)),
    ]

    payoffs = [
        ("AsianCall", AsianCallPayoff),
        ("AsianPut", AsianPutPayoff),
        ("LookbackCall", LookbackCallPayoff),
        ("LookbackPut", LookbackPutPayoff),
    ]

    header = f"{'Payoff':<15}{'Case':<6}{'Price':>12}{'StdErr':>12}{'Time(s)':>10}"
    print(header)
    print('-' * len(header))

    for name, payoff_cls in payoffs:
        for case, S0 in scenarios:
            payoff = payoff_cls(args.K)
            pricer = EuropeanPricer(
                model, payoff,
                n_paths=args.n_paths,
                n_steps=args.n_steps,
                seed=args.seed
            )
            t0 = time.time()
            price, stderr = pricer.price(S0, args.T, args.r)
            dt = time.time() - t0
            print(f"{name:<15}{case:<6}{price:12.6f}{stderr:12.6f}{dt:10.4f}")


if __name__ == "__main__":
    main()
