#!/usr/bin/env python3
"""
Download end-of-day (EOD) stock data for multiple tickers using yfinance,
compute minimum-variance and maximum-Sharpe (tangency) portfolios,
and report portfolio weights and performance statistics.

Dependencies: numpy, pandas, yfinance, scipy, matplotlib

Usage:
    python eod_portfolio_optimizer.py [--tickers AAPL MSFT NFLX]
                                      [--start YYYY-MM-DD] [--end YYYY-MM-DD]
                                      [--period PERIOD]
                                      [--risk-free-rate RF]
                                      [--annualize-days N]
                                      [--allow-shorts]

Options:
    --tickers             List of ticker symbols (default: AAPL MSFT NFLX)
    --start               Start date in YYYY-MM-DD format (default: 1 year ago if --period is not set)
    --end                 End date in YYYY-MM-DD format (default: today if --period is not set)
    --period              Data period (e.g., 1y, 6mo). Overrides --start/--end when set.
    --risk-free-rate      Annual risk-free rate in decimal (default: 0.0).
    --annualize-days      Trading days per year for annualization (default: 252).
    --allow-shorts        Allow short sales (weights can be negative). Default: no short sales.

Example:
    python eod_portfolio_optimizer.py --tickers GOOG AMZN TSLA --period 6mo --risk-free-rate 0.01 --allow-shorts
"""

import argparse
import datetime as dt

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.optimize import minimize


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute minimum-variance and max-Sharpe portfolios."
    )
    parser.add_argument(
        "-t", "--tickers",
        nargs="+",
        default=["AAPL", "MSFT", "NFLX"],
        help="Ticker symbols (default: AAPL MSFT NFLX)",
    )
    parser.add_argument(
        "--start",
        type=str,
        default=None,
        help="Start date YYYY-MM-DD (ignored if --period is set)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="End date YYYY-MM-DD (ignored if --period is set)",
    )
    parser.add_argument(
        "--period",
        type=str,
        default=None,
        help="Data period (e.g., 1y, 6mo). Overrides --start/--end when set.",
    )
    parser.add_argument(
        "--risk-free-rate",
        type=float,
        default=0.0,
        help="Annual risk-free rate in decimal (default: 0.0).",
    )
    parser.add_argument(
        "--annualize-days",
        type=int,
        default=252,
        help="Trading days per year for annualization (default: 252).",
    )
    parser.add_argument(
        "--allow-shorts",
        action="store_true",
        help="Allow short sales (weights can be negative). Default: no short sales.",
    )
    parser.add_argument(
        "--num-portfolios",
        type=int,
        default=500,
        help="Number of random portfolios to simulate (default: 500).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.period:
        data = yf.download(
            args.tickers,
            period=args.period,
            group_by="ticker",
        )
    else:
        end_date = args.end or dt.datetime.today().strftime("%Y-%m-%d")
        start_date = args.start or (
            dt.datetime.today() - dt.timedelta(days=365)
        ).strftime("%Y-%m-%d")
        data = yf.download(
            args.tickers,
            start=start_date,
            end=end_date,
            group_by="ticker",
        )

    if isinstance(data.columns, pd.MultiIndex):
        # for multi-ticker download, select the 'Close' level
        prices = data.xs("Close", level=1, axis=1)
    else:
        # single-ticker download yields flat columns
        prices = data["Close"].to_frame()
        prices.columns = args.tickers

    returns = prices.pct_change().dropna()

    ann_returns = returns.mean() * args.annualize_days
    ann_cov = returns.cov() * args.annualize_days

    ones = np.ones(len(ann_returns))
    inv_cov = np.linalg.inv(ann_cov.values)

    if args.allow_shorts:
        # Unconstrained closed-form solutions (shorts allowed)
        w_mvp = inv_cov.dot(ones) / ones.dot(inv_cov).dot(ones)
        excess_returns = ann_returns.values - args.risk_free_rate
        w_tan = inv_cov.dot(excess_returns) / ones.dot(inv_cov).dot(excess_returns)
    else:
        # No short sales: constrained optimization (weights >= 0, sum to 1)
        n = len(ann_returns)
        bounds = tuple((0.0, 1.0) for _ in range(n))
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1},)

        # minimum-variance
        def portfolio_variance(w):
            return w.dot(ann_cov.values).dot(w)

        init = ones / n
        res_mvp = minimize(portfolio_variance, init, bounds=bounds, constraints=constraints)
        w_mvp = res_mvp.x

        # maximum-Sharpe (tangency)
        def neg_sharpe(w):
            ret = w.dot(ann_returns.values)
            vol = np.sqrt(w.dot(ann_cov.values).dot(w))
            return -(ret - args.risk_free_rate) / vol

        res_tan = minimize(neg_sharpe, init, bounds=bounds, constraints=constraints)
        w_tan = res_tan.x

    def portfolio_stats(weights):
        ret = weights.dot(ann_returns.values)
        vol = np.sqrt(weights.dot(ann_cov.values).dot(weights))
        sharpe = (ret - args.risk_free_rate) / vol
        return ret, vol, sharpe

    ret_mvp, vol_mvp, sharpe_mvp = portfolio_stats(w_mvp)
    ret_tan, vol_tan, sharpe_tan = portfolio_stats(w_tan)

    weights_df = pd.DataFrame(
        {"Minimum Variance": w_mvp, "Max Sharpe": w_tan},
        index=ann_returns.index
    )
    print("\nPortfolio Weights:")
    print(weights_df)

    stats_df = pd.DataFrame(
        {
            "Expected Return": [ret_mvp, ret_tan],
            "Volatility": [vol_mvp, vol_tan],
            "Sharpe Ratio": [sharpe_mvp, sharpe_tan],
        },
        index=["Minimum Variance", "Max Sharpe"]
    )
    print("\nPortfolio Performance:")
    print(stats_df)

    # Plot normalized price series
    plt.figure(figsize=(10, 6))
    norm_prices = prices / prices.iloc[0]
    for ticker in norm_prices.columns:
        plt.plot(norm_prices.index, norm_prices[ticker], label=ticker)
    plt.title("Normalized Price Series for " + ", ".join(prices.columns))
    plt.xlabel("Date")
    plt.ylabel("Normalized Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Plot portfolio weights (pie charts when no shorts allowed, bar chart otherwise)
    if args.allow_shorts:
        weights_df.plot(kind="bar", figsize=(8, 6))
        plt.title("Portfolio Weights: Min Variance vs Max Sharpe")
        plt.ylabel("Weight")
        plt.grid(True, axis="y")
        plt.tight_layout()
    else:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        weights_df["Minimum Variance"].plot(
            kind="pie", ax=axes[0], autopct="%.1f%%", startangle=90
        )
        axes[0].set_title("Min Variance Weights")
        axes[0].set_ylabel("")
        weights_df["Max Sharpe"].plot(
            kind="pie", ax=axes[1], autopct="%.1f%%", startangle=90
        )
        axes[1].set_title("Max Sharpe Weights")
        axes[1].set_ylabel("")
        plt.tight_layout()

    # Monte Carlo simulation of random portfolios
    n_sim = args.num_portfolios
    mc_results = np.zeros((n_sim, 2))  # columns: volatility, return
    for i in range(n_sim):
        if args.allow_shorts:
            w = np.random.randn(len(ann_returns))
            w /= np.sum(w)
        else:
            w = np.random.rand(len(ann_returns))
            w /= np.sum(w)
        r = w.dot(ann_returns.values)
        v = np.sqrt(w.dot(ann_cov.values).dot(w))
        mc_results[i] = [v, r]

    # Plot Monte Carlo portfolios in risk-return space
    plt.figure(figsize=(8, 6))
    plt.scatter(mc_results[:, 0], mc_results[:, 1], c='gray', alpha=0.5, label='Simulated')
    plt.scatter(vol_mvp, ret_mvp, marker='*', color='red', s=200, label='Min Variance')
    plt.scatter(vol_tan, ret_tan, marker='*', color='blue', s=200, label='Max Sharpe')
    plt.xlabel('Volatility')
    plt.ylabel('Expected Return')
    plt.title(f'Monte Carlo Portfolios (n={n_sim})')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()