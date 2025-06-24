#!/usr/bin/env python3
"""
Streamlit web app for SMA crossover backtesting.

Dependencies:
    pip install streamlit yfinance matplotlib numpy python-dateutil

Usage:
    streamlit run sma_browser.py
"""

import streamlit as st
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

from datetime import date
from dateutil.relativedelta import relativedelta


def main():
    st.title("SMA Crossover Backtest")

    st.sidebar.header("Parameters")
    ticker = st.sidebar.text_input("Ticker", "SPY").upper()
    months = st.sidebar.number_input(
        "Months to retrieve", min_value=1, value=36, step=1
    )
    fast_window = st.sidebar.number_input(
        "Fast SMA window (days)", min_value=1, value=20, step=1
    )
    slow_window = st.sidebar.number_input(
        "Slow SMA window (days)", min_value=1, value=50, step=1
    )
    strategy_type = st.sidebar.selectbox(
        "Strategy type", ["long-only", "long-short"]
    )

    if fast_window >= slow_window:
        st.sidebar.error("Fast SMA window must be less than slow SMA window.")
        return

    end_date = date.today()
    start_date = end_date - relativedelta(months=months)
    st.write(f"Downloading data for {ticker} from {start_date} to {end_date}...")
    data = yf.download(ticker, start=start_date, end=end_date)

    if data.empty:
        st.error(f"No data found for ticker '{ticker}'.")
        return

    data[f"SMA_{fast_window}"] = data["Close"].rolling(window=fast_window).mean()
    data[f"SMA_{slow_window}"] = data["Close"].rolling(window=slow_window).mean()

    df_bt = data[["Close", f"SMA_{fast_window}", f"SMA_{slow_window}"]].dropna().copy()
    df_bt["return"] = df_bt["Close"].pct_change().fillna(0)

    if strategy_type == "long-only":
        df_bt["position"] = (
            df_bt[f"SMA_{fast_window}"] > df_bt[f"SMA_{slow_window}"]
        ).astype(int)
        strat_label = "Crossover Strategy (long-only)"
    else:
        df_bt["position"] = np.where(
            df_bt[f"SMA_{fast_window}"] > df_bt[f"SMA_{slow_window}"], 1, -1
        )
        strat_label = "Crossover Strategy (long-short)"
    df_bt["position"] = df_bt["position"].shift(1).fillna(0)

    df_bt["strategy_return"] = df_bt["return"] * df_bt["position"]
    df_bt["cum_benchmark"] = (1 + df_bt["return"]).cumprod()
    df_bt["cum_strategy"] = (1 + df_bt["strategy_return"]).cumprod()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
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
        label=f"SMA {fast_window}",
        color=color_fast,
        linestyle="--",
        lw=1,
    )
    ax1.plot(
        data.index,
        data[f"SMA_{slow_window}"],
        label=f"SMA {slow_window}",
        color=color_slow,
        linestyle="--",
        lw=1,
    )
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
    ax1.set_ylabel("Price (USD)")
    ax1.set_title(f"{ticker} Price & SMAs")
    ax1.grid(True)
    ax1.legend()

    ax2.plot(df_bt.index, df_bt["cum_benchmark"], label="Buy & Hold", color=color_bh)
    ax2.plot(df_bt.index, df_bt["cum_strategy"], label=strat_label, color=color_strat)
    final_bh = df_bt["cum_benchmark"].iloc[-1]
    final_strat = df_bt["cum_strategy"].iloc[-1]
    perf_text = f"Buy & Hold: {final_bh:.2f}\n{strat_label}: {final_strat:.2f}"
    ax2.text(
        0.02,
        0.95,
        perf_text,
        transform=ax2.transAxes,
        va="top",
        ha="left",
        bbox=dict(facecolor="white", edgecolor="black", linewidth=1, alpha=0.8),
    )
    ax2.set_xlabel("Date")
    ax2.set_ylabel("Growth of $1")
    ax2.set_title("Cumulative Returns")
    ax2.grid(True)
    ax2.legend(loc="lower right")

    plt.tight_layout()
    st.pyplot(fig)


if __name__ == "__main__":
    main()