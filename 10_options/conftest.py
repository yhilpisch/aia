"""
Top-level pytest configuration: ensure project root is on PYTHONPATH for imports.
"""
import os
import sys

# Add project root to sys.path so tests can import option_pricing package
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))