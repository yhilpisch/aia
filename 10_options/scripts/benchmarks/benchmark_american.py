#!/usr/bin/env python3
"""
Benchmark American option pricing (LSM MC vs CRR binomial) for ITM, ATM, and OTM cases.
"""

import os
import sys
import time
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import numpy as np
from option_pricing.models import BSM
from option_pricing.payoffs import CallPayoff, PutPayoff
from option_pricing.pricers.european import EuropeanPricer
from option_pricing.pricers.american import AmericanBinomialPricer, LongstaffSchwartzPricer


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark American exercise pricing: MC (LSM) vs CRR binomial"
    )
    parser.add_argument("--K", type=float, default=100.0, help="Strike price")
    parser.add_argument("--T", type=float, default=1.0, help="Time to maturity")
    parser.add_argument("--r", type=float, default=0.05, help="Risk-free rate")
    parser.add_argument("--sigma", type=float, default=0.2, help="Volatility")
    parser.add_argument(
        "--n_paths", type=int, default=100000, help="Number of Monte Carlo paths"
    )
    parser.add_argument(
        "--n_steps", type=int, default=50, help="Number of time steps per path"
    )
    parser.add_argument("--n_tree", type=int, default=200, help="Number of binomial steps")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--q", type=float, default=0.0, help="Dividend yield")
    args = parser.parse_args()

    model = BSM(args.r, args.sigma, q=args.q)
    moneyness = 0.10
    scenarios = []
    for opt_type, payoff_cls in [("call", CallPayoff), ("put", PutPayoff)]:
        if opt_type == "call":
            S0_cases = [args.K * (1 + moneyness), args.K, args.K * (1 - moneyness)]
        else:
            S0_cases = [args.K * (1 - moneyness), args.K, args.K * (1 + moneyness)]
        for case, S0_case in zip(["ITM", "ATM", "OTM"], S0_cases):
            scenarios.append((opt_type, payoff_cls, case, S0_case))

    header = f"{'Type':<6}{'Case':<6}{'MC Price':>12}{'StdErr':>12}{'CRR Price':>12}{'Abs Err':>12}{'% Err':>10}{'MC Time(s)':>12}{'Tree Time(s)':>12}"
    print(header)
    print('-' * len(header))

    for opt_type, payoff_cls, case, S0_case in scenarios:
        payoff = payoff_cls(args.K)
        # LSM Monte Carlo
        lsm = LongstaffSchwartzPricer(
            model, payoff, n_paths=args.n_paths, n_steps=args.n_steps, seed=args.seed
        )
        t0 = time.time()
        price_mc, stderr = lsm.price(S0_case, args.T, args.r)
        t_mc = time.time() - t0

        # CRR binomial
        binom = AmericanBinomialPricer(model, payoff, n_steps=args.n_tree)
        t0 = time.time()
        price_crr = binom.price(S0_case, args.T, args.r)
        t_crr = time.time() - t0

        abs_err = abs(price_mc - price_crr)
        pct_err = abs_err / price_crr * 100.0 if price_crr != 0 else float('nan')
        print(f"{opt_type.capitalize():<6}{case:<6}{price_mc:12.6f}{stderr:12.6f}{price_crr:12.6f}{abs_err:12.6f}{pct_err:10.2f}{t_mc:12.4f}{t_crr:12.4f}")


if __name__ == "__main__":
    main()
