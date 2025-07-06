#!/usr/bin/env python

import argparse
import os
import sys
import importlib.util
import inspect

# Ensure parent directory is in sys.path for importing option_pricing package
sys_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Orchestrate valuation benchmarks using valuation_functions modules"
    )
    parser.add_argument("--S0", type=float, default=100.0,
                        help="Initial spot price")
    parser.add_argument("--K", type=float, default=100.0,
                        help="Strike price")
    parser.add_argument("--T", type=float, default=1.0,
                        help="Time to maturity")
    parser.add_argument("--r", type=float, default=0.05,
                        help="Risk-free rate")
    parser.add_argument("--sigma", type=float, default=0.2,
                        help="Volatility")
    parser.add_argument("--q", type=float, default=0.0,
                        help="Dividend yield")
    parser.add_argument("--n_paths", type=int, default=100000,
                        help="Number of Monte Carlo paths")
    parser.add_argument("--n_steps", type=int, default=50,
                        help="Number of time steps per path")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    parser.add_argument("--n_tree", type=int, default=200,
                        help="Number of steps for CRR binomial tree")
    parser.add_argument("--lam", type=float, default=0.3,
                        help="Jump intensity (lambda) for Merton model")
    parser.add_argument("--mu_j", type=float, default=-0.1,
                        help="Mean jump size (mu_j) for Merton model")
    parser.add_argument("--sigma_j", type=float, default=0.2,
                        help="Jump volatility (sigma_j) for Merton model")
    parser.add_argument("--kappa", type=float, default=2.0,
                        help="Heston mean reversion speed")
    parser.add_argument("--theta", type=float, default=0.04,
                        help="Heston long-run variance")
    parser.add_argument("--xi", type=float, default=0.2,
                        help="Heston vol-of-vol xi")
    parser.add_argument("--rho", type=float, default=-0.5,
                        help="Heston correlation rho")
    parser.add_argument("--v0", type=float, default=0.02,
                        help="Heston initial variance")
    return parser.parse_args()

def load_valuation_functions(val_dir):
    funcs = []
    for fname in sorted(os.listdir(val_dir)):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        module_name = fname[:-3]
        file_path = os.path.join(val_dir, fname)
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # find the first function that starts with 'value_'
        for attr in dir(module):
            if attr.startswith("value_"):
                func = getattr(module, attr)
                funcs.append((module_name, func))
                break
    return funcs

def main():
    args = parse_args()

    # define scenarios: ITM, ATM, OTM
    moneyness = 0.10
    scenarios = []
    for opt_type in ["call", "put"]:
        if opt_type == "call":
            scenarios.append(("ITM", opt_type, args.K * (1 + moneyness)))
            scenarios.append(("ATM", opt_type, args.K))
            scenarios.append(("OTM", opt_type, args.K * (1 - moneyness)))
        else:
            scenarios.append(("ITM", opt_type, args.K * (1 - moneyness)))
            scenarios.append(("ATM", opt_type, args.K))
            scenarios.append(("OTM", opt_type, args.K * (1 + moneyness)))

    # load valuation functions
    script_dir = os.path.dirname(__file__)
    val_dir = os.path.join(script_dir, "valuation_functions")
    funcs = load_valuation_functions(val_dir)
    if not funcs:
        print(f"No valuation functions found in {val_dir}")
        sys.exit(1)

    # run benchmarks
    for module_name, func in funcs:
        print(f"\n{module_name.replace('_', ' ').title()} Benchmark:")

        # determine return labels based on module_name
        if module_name == "european_bsm":
            ret_labels = ["MCS", "StdErr", "BS Price", "Abs Err", "% Err", "MC Time(s)"]
        elif module_name == "european_merton":
            ret_labels = ["MCS", "StdErr", "Analytic", "Abs Err", "% Err", "MC Time(s)"]
        elif module_name == "european_heston":
            ret_labels = ["MCS", "StdErr", "Analytic", "Abs Err", "% Err", "MC Time(s)"]
        elif module_name == "american_lsm_crr":
            ret_labels = ["LSM Price", "StdErr", "CRR Price", "Abs Err", "% Err", "MC Time(s)", "Tree Time(s)"]
        else:
            print(f"Skipping unrecognized module: {module_name}")
            continue

        # print header with fixed-width columns
        header = f"{'Type':<6}{'Case':<6}" + "".join(f"{label:>13}" for label in ret_labels)
        print(header)
        print('-' * len(header))

        # call function for each scenario
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        for case, opt_type, S0_case in scenarios:
            # prepare kwargs
            kwargs = {p: getattr(args, p) for p in params if hasattr(args, p)}
            kwargs['S0'] = S0_case
            kwargs['opt_type'] = opt_type
            res = func(**kwargs)

            # print values with matching column widths
            line = f"{opt_type:<6}{case:<6}"
            for v in res:
                if isinstance(v, float):
                    line += f"{v:13.6f}"
                else:
                    line += f"{str(v):>13}"
            print(line)

if __name__ == "__main__":
    main()
