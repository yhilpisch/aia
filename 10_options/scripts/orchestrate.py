#!/usr/bin/env python3
"""
Orchestrate all benchmark suites: BSM, Merton jump-diffusion, Heston, and American.
"""

import os
import sys
import subprocess
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Orchestrate all benchmark suites: BSM, MJD, Bates, Heston, American"
    )
    # global flags for any benchmark
    parser.add_argument("--K", type=float, help="Strike price")
    parser.add_argument("--T", type=float, help="Time to maturity")
    parser.add_argument("--r", type=float, help="Risk-free rate")
    parser.add_argument("--sigma", type=float, help="Volatility")
    parser.add_argument("--lam", type=float, help="Jump intensity (lambda)")
    parser.add_argument("--mu_j", type=float, help="Jump mean mu_j")
    parser.add_argument("--sigma_j", type=float, help="Jump volatility sigma_j")
    parser.add_argument("--kappa", type=float, help="Heston mean-reversion speed kappa")
    parser.add_argument("--theta", type=float, help="Heston long-term variance theta")
    parser.add_argument("--xi", type=float, help="Heston vol-of-vol xi")
    parser.add_argument("--rho", type=float, help="Heston correlation rho")
    parser.add_argument("--v0", type=float, help="Initial variance v0")
    parser.add_argument("--n_paths", type=int, help="Number of Monte Carlo paths")
    parser.add_argument("--n_steps", type=int, help="Number of time steps per path")
    parser.add_argument("--n_tree", type=int, help="Number of binomial steps")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--q", type=float, help="Dividend yield")
    args = parser.parse_args()

    scripts = [
        'benchmarks/benchmark_bsm.py',
        'benchmarks/benchmark_mjd.py',
        'benchmarks/benchmark_bates.py',
        'benchmarks/benchmark_heston.py',
        'benchmarks/benchmark_american.py',
    ]
    # which flags apply to each benchmark
    script_args = {
        'benchmark_bsm.py': ["K","T","r","sigma","n_paths","n_steps","seed","q"],
        'benchmark_mjd.py': ["K","T","r","sigma","lam","mu_j","sigma_j","n_paths","n_steps","seed","q"],
        'benchmark_bates.py': ["K","T","r","kappa","theta","xi","rho","v0","lam","mu_j","sigma_j","n_paths","n_steps","seed","q"],
        'benchmark_heston.py': ["K","T","r","kappa","theta","xi","rho","v0","n_paths","n_steps","seed","q"],
        'benchmark_american.py': ["K","T","r","sigma","n_paths","n_steps","n_tree","seed","q"],
    }
    here = os.path.dirname(__file__)
    for script in scripts:
        path = os.path.join(here, script)
        print(f"\nRunning {script}...\n")
        cmd = [sys.executable, path]
        name = os.path.basename(script)
        for key in script_args.get(name, []):
            val = getattr(args, key)
            if val is not None:
                cmd += [f"--{key}", str(val)]
        subprocess.run(cmd)


if __name__ == '__main__':
    main()
