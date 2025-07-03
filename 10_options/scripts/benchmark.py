#!/usr/bin/env python
"""
Benchmark Monte Carlo European option pricing vs analytical BSM and
CRR binomial American option pricing (ATM/ITM/OTM scenarios).
"""

import os
import sys
import time
import math
import numpy as np
import argparse

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
from option_pricing.models import BSM, MertonJumpDiffusion, Heston
from option_pricing.payoffs import CallPayoff, PutPayoff
from option_pricing.pricers.european import EuropeanPricer
from option_pricing.pricers.american import AmericanBinomialPricer, LongstaffSchwartzPricer
from option_pricing.analytics import norm_cdf, bsm_price, merton_price, heston_price


def main():
    parser = argparse.ArgumentParser(
        description="MC European/American vs. BSM and CRR American option pricing benchmark"
    )
    parser.add_argument("--S0", type=float, default=100.0,
                        help="Initial spot price")
    parser.add_argument("--K", type=float, default=100.0, help="Strike price")
    parser.add_argument("--T", type=float, default=1.0,
                        help="Time to maturity")
    parser.add_argument("--r", type=float, default=0.05, help="Risk-free rate")
    parser.add_argument("--sigma", type=float, default=0.2, help="Volatility")
    parser.add_argument(
        "--n_paths", type=int, default=100000, help="Number of Monte Carlo paths"
    )
    parser.add_argument(
        "--n_steps", type=int, default=50, help="Number of time steps per path"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--n_tree", type=int, default=200,
        help="Number of steps for CRR binomial tree pricing"
    )
    parser.add_argument(
        "--lam", type=float, default=0.3,
        help="Jump intensity (lambda) for Merton jump-diffusion"
    )
    parser.add_argument(
        "--mu_j", type=float, default=-0.1,
        help="Mean jump size (lognormal mu_j) for Merton model"
    )
    parser.add_argument(
        "--sigma_j", type=float, default=0.2,
        help="Jump size volatility (sigma_j) for Merton model"
    )
    parser.add_argument("--q", type=float, default=0.0,
                        help="Dividend yield"
                        )
    parser.add_argument(
        "--kappa", type=float, default=2.0,
        help="Mean-reversion speed for Heston model"
    )
    parser.add_argument(
        "--theta", type=float, default=0.04,
        help="Long-run variance theta for Heston model"
    )
    parser.add_argument(
        "--xi", type=float, default=0.2,
        help="Vol-of-vol xi for Heston model"
    )
    parser.add_argument(
        "--rho", type=float, default=-0.5,
        help="Correlation rho for Heston model"
    )
    parser.add_argument(
        "--v0", type=float, default=0.02,
        help="Initial variance v0 for Heston model"
    )
    args = parser.parse_args()

    model = BSM(args.r, args.sigma, q=args.q)
    # jump-diffusion model for Merton series benchmark
    model_mjd = MertonJumpDiffusion(
        args.r, args.sigma, args.lam, args.mu_j, args.sigma_j, q=args.q
    )
    # Define scenarios: ATM, ITM and OTM with a fixed moneyness percentage
    moneyness = 0.10
    scenarios = []
    for opt_type, payoff_cls in [("call", CallPayoff), ("put", PutPayoff)]:
        scenarios.append((opt_type, payoff_cls, "ATM", args.K))
        # ITM and OTM by moneyness
        if opt_type == "call":
            scenarios.append(
                (opt_type, payoff_cls, "ITM", args.K * (1 + moneyness)))
            scenarios.append(
                (opt_type, payoff_cls, "OTM", args.K * (1 - moneyness)))
        else:
            scenarios.append(
                (opt_type, payoff_cls, "ITM", args.K * (1 - moneyness)))
            scenarios.append(
                (opt_type, payoff_cls, "OTM", args.K * (1 + moneyness)))

    # 1) European options: MC vs analytical BSM
    results_eur = []
    for opt_type, payoff_cls, case, S0_case in scenarios:
        payoff = payoff_cls(args.K)
        eur_mc = EuropeanPricer(model, payoff,
                                n_paths=args.n_paths,
                                n_steps=args.n_steps,
                                seed=args.seed)
        t0 = time.time()
        price_mc, stderr = eur_mc.price(S0_case, args.T, args.r)
        t_mc = time.time() - t0

        price_bs = bsm_price(
            S0_case, args.K, args.T, args.r, args.sigma,
            option_type=opt_type
        )

        abs_err = abs(price_mc - price_bs)
        pct_err = abs_err / price_bs * 100.0 if price_bs != 0 else float("nan")
        results_eur.append((opt_type.capitalize(), case,
                            price_mc, price_bs,
                            abs_err, pct_err, t_mc))

    # Print European results
    print("\nEuropean option pricing (MC vs BSM):")
    header_eur = (
        f"{'Type':<6}{'Case':<6}"
        f"{'MC Price':>12}{'BSM Price':>12}{'Abs Err':>12}{'% Err':>10}{'MC Time(s)':>12}"
    )
    print(header_eur)
    print('-' * len(header_eur))
    for typ, case, mc, bsm, err, pct, tmc in results_eur:
        print(
            f"{typ:<6}{case:<6}{mc:12.6f}{bsm:12.6f}"
            f"{err:12.6f}{pct:10.2f}{tmc:12.4f}"
        )

    # 2) Merton jump-diffusion European options: MC vs analytic
    results_mjd = []
    for opt_type, payoff_cls, case, S0_case in scenarios:
        payoff = payoff_cls(args.K)
        mjd_mc = EuropeanPricer(
            model_mjd, payoff,
            n_paths=args.n_paths,
            n_steps=args.n_steps,
            seed=args.seed
        )
        t0 = time.time()
        price_mc_jd, stderr_jd = mjd_mc.price(S0_case, args.T, args.r)
        t_mc_jd = time.time() - t0

        price_call_jd = merton_price(
            S0_case, args.K, args.T, args.r, args.sigma,
            args.lam, args.mu_j, args.sigma_j
        )
        if opt_type == 'call':
            price_anal_jd = price_call_jd
        else:
            price_anal_jd = (
                price_call_jd
                - S0_case * math.exp(-args.q * args.T)
                + args.K * math.exp(-args.r * args.T)
            )

        abs_err_jd = abs(price_mc_jd - price_anal_jd)
        pct_err_jd = abs_err_jd / price_anal_jd * \
            100.0 if price_anal_jd != 0 else float('nan')
        results_mjd.append((
            opt_type.capitalize(), case,
            price_mc_jd, price_anal_jd,
            abs_err_jd, pct_err_jd,
            t_mc_jd
        ))

    print("\nMerton jump-diffusion European (MC vs analytic):")
    header_mjd = (
        f"{'Type':<6}{'Case':<6}"
        f"{'MC Price':>12}{'Analytic':>12}{'Abs Err':>12}{'% Err':>10}{'MC Time(s)':>12}"
    )
    print(header_mjd)
    print('-' * len(header_mjd))
    for typ, case, mc, an, err, pct, tmc in results_mjd:
        print(
            f"{typ:<6}{case:<6}{mc:12.6f}{an:12.6f}"
            f"{err:12.6f}{pct:10.2f}{tmc:12.4f}"
        )

    # 3) Heston stochastic-volatility European options: MC vs semi-analytic
    model_hes = Heston(
        args.r, args.kappa, args.theta,
        args.xi, args.rho, args.v0, q=args.q
    )
    results_hes = []
    for opt_type, payoff_cls, case, S0_case in scenarios:
        payoff = payoff_cls(args.K)
        hes_mc = EuropeanPricer(
            model_hes, payoff,
            n_paths=args.n_paths,
            n_steps=args.n_steps,
            seed=args.seed
        )
        t0 = time.time()
        price_mc_hes, stderr_hes = hes_mc.price(S0_case, args.T, args.r)
        t_mc_hes = time.time() - t0

        price_an_hes = heston_price(
            S0_case, args.K, args.T, args.r, args.q,
            args.kappa, args.theta, args.xi, args.rho, args.v0
        )

        abs_err = abs(price_mc_hes - price_an_hes)
        pct_err = abs_err / price_an_hes * \
            100.0 if price_an_hes != 0 else float('nan')
        results_hes.append((
            opt_type.capitalize(), case,
            price_mc_hes, price_an_hes,
            abs_err, pct_err,
            t_mc_hes
        ))

    print("\nHeston SV model European (MC vs semi-analytic):")
    header_hes = (
        f"{'Type':<6}{'Case':<6}"
        f"{'MC Price':>12}{'Analytic':>14}{'Abs Err':>12}{'% Err':>10}{'MC Time(s)':>12}"
    )
    print(header_hes)
    print('-' * len(header_hes))
    for typ, case, mc, an, err, pct, tmc in results_hes:
        print(
            f"{typ:<6}{case:<6}{mc:12.6f}{an:14.6f}"
            f"{err:12.6f}{pct:10.2f}{tmc:12.4f}"
        )

    # 4) American options: MC (LSM) vs CRR binomial
    results_amer = []
    for opt_type, payoff_cls, case, S0_case in scenarios:
        payoff = payoff_cls(args.K)
        am_mc = LongstaffSchwartzPricer(model, payoff,
                                        n_paths=args.n_paths,
                                        n_steps=args.n_steps,
                                        seed=args.seed)
        t0 = time.time()
        price_am_mc, stderr_am = am_mc.price(S0_case, args.T, args.r)
        t_mc_am = time.time() - t0

        am_crr = AmericanBinomialPricer(model, payoff, n_steps=args.n_tree)
        t0 = time.time()
        price_crr = am_crr.price(S0_case, args.T, args.r)
        t_crr = time.time() - t0

        abs_err = abs(price_am_mc - price_crr)
        pct_err = abs_err / price_crr * \
            100.0 if price_crr != 0 else float("nan")
        results_amer.append((opt_type.capitalize(), case,
                             price_am_mc, price_crr,
                             abs_err, pct_err,
                             t_mc_am, t_crr))

    # Print American results
    print("\nAmerican option pricing (LSM MC vs CRR):")
    header_amer = (
        f"{'Type':<6}{'Case':<6}"
        f"{'MC Price':>12}{'CRR Price':>12}{'Abs Err':>12}{'% Err':>10}"
        f"{'MC Time(s)':>12} {'Tree Time(s)':>12}"
    )
    print(header_amer)
    print('-' * len(header_amer))
    for typ, case, mc, crr, err, pct, tmc, tcrr in results_amer:
        print(
            f"{typ:<6}{case:<6}{mc:12.6f}{crr:12.6f}"
            f"{err:12.6f}{pct:10.2f}{tmc:12.4f} {tcrr:12.4f}"
        )


if __name__ == "__main__":
    main()
