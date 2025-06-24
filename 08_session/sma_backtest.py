#!/usr/bin/env python3
"""Fetch and visualize historical stock data using yfinance.

Prompts the user for:
  - a ticker symbol
  - number of months to retrieve
  - two SMA window values (fast and slow)
  - a strategy type ('long-only' or 'long-short')

Retrieves data for that period, visualizes closing price and SMAs, marks crossovers,
and backtests the specified crossover strategy vs. buy & hold.
"""

import datetime
from dateutil.relativedelta import relativedelta
import sys

import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np


def main():
    ticker = input("Enter ticker symbol (e.g. SPY): ").strip().upper()

    try:
        months = int(input(
            "Enter number of months to retrieve data for (e.g. 36 for 3 years): "
        ).strip())
    except ValueError:
        print("Invalid input: number of months must be an integer. Exiting.")
        sys.exit(1)

    if months <= 0:
        print("Number of months must be positive. Exiting.")
        sys.exit(1)

    try:
        fast_window = int(input("Enter fast SMA window (days, e.g. 20): ").strip())
        slow_window = int(input("Enter slow SMA window (days, e.g. 50): ").strip())
    except ValueError:
        print("Invalid input: SMA windows must be integers. Exiting.")
        sys.exit(1)

    if fast_window <= 0 or slow_window <= 0:
        print("SMA windows must be positive integers. Exiting.")
        sys.exit(1)

    strategy_type = input("Enter strategy type ('long-only' or 'long-short'): ").strip().lower()
    if strategy_type not in ('long-only', 'long-short'):
        print("Invalid strategy type. Exiting.")
        sys.exit(1)

    end_date = datetime.date.today()
    start_date = end_date - relativedelta(months=months)

    print(f"Downloading data for {ticker} from {start_date} to {end_date}...")
    data = yf.download(ticker, start=start_date, end=end_date)

    if data.empty:
        print(f"No data found for ticker symbol '{ticker}'. Exiting.")
        sys.exit(1)

    data[f"SMA_{fast_window}"] = data["Close"].rolling(window=fast_window).mean()
    data[f"SMA_{slow_window}"] = data["Close"].rolling(window=slow_window).mean()

    # Backtest setup: only keep entries where both SMAs exist
    df_bt = data[["Close", f"SMA_{fast_window}", f"SMA_{slow_window}"]].dropna().copy()
    # Compute daily returns
    df_bt["return"] = df_bt["Close"].pct_change().fillna(0)
    # Determine positions based on strategy type
    if strategy_type == 'long-only':
        df_bt["position"] = (
            df_bt[f"SMA_{fast_window}"] > df_bt[f"SMA_{slow_window}"]
        ).astype(int)
    else:
        # long-short: long when fast > slow, short when fast < slow
        df_bt["position"] = np.where(
            df_bt[f"SMA_{fast_window}"] > df_bt[f"SMA_{slow_window}"], 1, -1
        )
    df_bt["position"] = df_bt["position"].shift(1).fillna(0)
    df_bt["strategy_return"] = df_bt["return"] * df_bt["position"]
    df_bt["cum_benchmark"] = (1 + df_bt["return"]).cumprod()
    df_bt["cum_strategy"] = (1 + df_bt["strategy_return"]).cumprod()
    strategy_label = (
        "Crossover Strategy (long-only)"
        if strategy_type == 'long-only'
        else "Crossover Strategy (long-short)"
    )

    # Plot price + SMAs with crossover markers, and performance
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Define colormap colors
    cmap = plt.get_cmap("coolwarm")
    color_price = cmap(0.0)
    color_fast = cmap(0.3)
    color_slow = cmap(0.7)
    color_bh = cmap(0.0)
    color_strat = cmap(1.0)

    ax1.plot(data.index, data["Close"], label="Close", color=color_price)
    ax1.plot(
        data.index,
        data[f"SMA_{fast_window}"],
        color=color_fast,
        linestyle="--",
        lw=1,
        label=f"SMA {fast_window}",
    )
    ax1.plot(
        data.index,
        data[f"SMA_{slow_window}"],
        color=color_slow,
        linestyle="--",
        lw=1,
        label=f"SMA {slow_window}",
    )
    # Mark crossovers
    fast_sma = data[f"SMA_{fast_window}"]
    slow_sma = data[f"SMA_{slow_window}"]
    cross_up = (fast_sma > slow_sma) & (fast_sma.shift(1) <= slow_sma.shift(1))
    cross_down = (fast_sma < slow_sma) & (fast_sma.shift(1) >= slow_sma.shift(1))
    ax1.scatter(
        data.index[cross_up], fast_sma[cross_up], marker="^", color=color_strat, s=50, zorder=5
    )
    ax1.scatter(
        data.index[cross_down], fast_sma[cross_down], marker="v", color="green", s=50, zorder=5
    )
    ax1.set_title(f"{ticker} Price & SMAs ({start_date} to {end_date})")
    ax1.set_ylabel("Price (USD)")
    ax1.grid(True)
    ax1.legend()

    ax2.plot(df_bt.index, df_bt["cum_benchmark"], label="Buy & Hold", color=color_bh)
    ax2.plot(df_bt.index, df_bt["cum_strategy"], label=strategy_label, color=color_strat)
    ax2.set_title("Cumulative Returns")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Growth of $1")
    # Annotate final performance in upper left, avoiding overlap
    final_bh = df_bt["cum_benchmark"].iloc[-1]
    final_strat = df_bt["cum_strategy"].iloc[-1]
    perf_text = (
        f"Buy & Hold: {final_bh:.2f}\n"
        f"{strategy_label}: {final_strat:.2f}"
    )
    ax2.text(
        0.02,
        0.95,
        perf_text,
        transform=ax2.transAxes,
        va="top",
        ha="left",
        bbox=dict(facecolor="white", edgecolor="black", linewidth=1, alpha=0.8),
    )
    ax2.grid(True)
    ax2.legend(loc="lower right")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()