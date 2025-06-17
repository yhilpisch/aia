#!/usr/bin/env python3
"""
fibonacci.py

Module providing an efficient iterative algorithm to compute Fibonacci numbers.

Author: The Python Quants GmbH
Copyright (c) 2025 The Python Quants GmbH
"""

__author__ = "The Python Quants GmbH"
__copyright__ = "Copyright (c) 2025 The Python Quants GmbH"
__version__ = "1.0.0"

def fib_it_py(n):
    """
    Calculate the n-th Fibonacci number using an iterative algorithm.

    Fibonacci sequence:
      F(0) = 0
      F(1) = 1
      F(n) = F(n-1) + F(n-2) for n >= 2

    Parameters
    ----------
    n : int
        Non-negative integer index of the desired Fibonacci number.

    Returns
    -------
    int
        The n-th Fibonacci number.

    Raises
    ------
    TypeError
        If n is not an integer.
    ValueError
        If n is a negative integer.
    """
    if not isinstance(n, int):
        raise TypeError(f"n must be an integer, got {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")

    x, y = 0, 1
    for _ in range(1, n + 1):
        x, y = y, x + y
    return x

import unittest

class TestFibItPy(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(fib_it_py(0), 0)

    def test_one(self):
        self.assertEqual(fib_it_py(1), 1)

    def test_small_numbers(self):
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
        for i, val in enumerate(expected):
            self.assertEqual(fib_it_py(i), val)

    def test_larger_number(self):
        self.assertEqual(fib_it_py(20), 6765)

    def test_type_error(self):
        with self.assertRaises(TypeError):
            fib_it_py(3.14)

    def test_value_error(self):
        with self.assertRaises(ValueError):
            fib_it_py(-5)

if __name__ == "__main__":
    unittest.main()
