#!/usr/bin/env python3
"""
Orchestrate all benchmark suites: BSM, Merton jump-diffusion, Heston, and American.
"""

import os
import sys
import subprocess


def main():
    scripts = [
        'benchmarks/benchmark_bsm.py',
        'benchmarks/benchmark_mjd.py',
        'benchmarks/benchmark_heston.py',
        'benchmarks/benchmark_american.py',
    ]
    here = os.path.dirname(__file__)
    for script in scripts:
        path = os.path.join(here, script)
        print(f"\nRunning {script}...\n")
        subprocess.run([sys.executable, path])


if __name__ == '__main__':
    main()
