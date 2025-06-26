#!/usr/bin/env python3
"""
Streamlit application for fetching EOD stock data, computing optimal portfolios,
and visualizing prices, allocations, and Monte Carlo risk-return simulations.
"""

import datetime as dt

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.optimize import minimize


@st.cache_data
def load_data(tickers, period, start_date, end_date):
    """
    Fetch EOD 'Close' prices for given tickers using yfinance.
    Caches results to speed up repeated queries.
    """
    if period:
        df = yf.download(tickers, period=period, group_by="ticker")
    else:
        df = yf.download(
            tickers,
            start=start_date,
            end=end_date,
            group_by="ticker",
        )
    # Extract close prices
    if isinstance(df.columns, pd.MultiIndex):
        prices = df.xs("Close", level=1, axis=1)
    else:
        prices = df["Close"].to_frame()
        prices.columns = tickers
    return prices


# Sidebar - user inputs
st.sidebar.title("Portfolio Optimizer Settings")
tickers_input = st.sidebar.text_input("Tickers (comma-separated)", "AAPL, MSFT, NFLX")
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

date_mode = st.sidebar.radio("Date range mode", ("Period", "Dates"))
if date_mode == "Period":
    period = st.sidebar.text_input("Period (e.g. 1y,6mo)", "1y")
    start_date = end_date = None
else:
    period = None
    start_date = st.sidebar.date_input("Start date", dt.date.today() - dt.timedelta(days=365))
    end_date = st.sidebar.date_input("End date", dt.date.today())

normalize = st.sidebar.checkbox("Normalize prices", value=True)
allow_shorts = st.sidebar.checkbox("Allow short sales", value=False)
num_portfolios = st.sidebar.slider("Number of simulations", 100, 5000, 500, step=100)
risk_free_rate = st.sidebar.number_input("Annual risk-free rate", min_value=0.0, max_value=1.0, value=0.0)
annualize_days = st.sidebar.number_input("Trading days/year", min_value=1, max_value=365, value=252)

st.title("📈 Portfolio Optimization Dashboard")

# Load data
prices = load_data(tickers, period, start_date, end_date)
st.write("### Closing Price Data", prices.round(4).tail())

# Compute returns and annualized metrics
returns = prices.pct_change().dropna()
ann_returns = returns.mean() * annualize_days
ann_cov = returns.cov() * annualize_days

# Portfolio optimization
ones = np.ones(len(ann_returns))
inv_cov = np.linalg.inv(ann_cov.values)
if allow_shorts:
    w_mvp = inv_cov.dot(ones) / ones.dot(inv_cov).dot(ones)
    excess = ann_returns.values - risk_free_rate
    w_tan = inv_cov.dot(excess) / ones.dot(inv_cov).dot(excess)
else:
    bounds = tuple((0.0, 1.0) for _ in range(len(ones)))
    constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1},)
    init = ones / len(ones)
    res_mvp = minimize(lambda w: w.dot(ann_cov.values).dot(w), init, bounds=bounds, constraints=constraints)
    w_mvp = res_mvp.x
    res_tan = minimize(
        lambda w: -((w.dot(ann_returns.values) - risk_free_rate) / np.sqrt(w.dot(ann_cov.values).dot(w))),
        init,
        bounds=bounds,
        constraints=constraints,
    )
    w_tan = res_tan.x

def port_stats(w):
    ret = w.dot(ann_returns.values)
    vol = np.sqrt(w.dot(ann_cov.values).dot(w))
    sharpe = (ret - risk_free_rate) / vol
    return ret, vol, sharpe

ret_mvp, vol_mvp, sharpe_mvp = port_stats(w_mvp)
ret_tan, vol_tan, sharpe_tan = port_stats(w_tan)

weights_df = pd.DataFrame({"Min Variance": w_mvp, "Max Sharpe": w_tan}, index=ann_returns.index)
stats_df = pd.DataFrame(
    {"Return": [ret_mvp, ret_tan], "Volatility": [vol_mvp, vol_tan], "Sharpe": [sharpe_mvp, sharpe_tan]},
    index=["Min Variance", "Max Sharpe"],
)

st.write("## Portfolio Weights", weights_df.round(4))
st.write("## Performance Metrics", stats_df.round(4))

# Visualization tabs
tab1, tab2, tab3 = st.tabs(["Price Series", "Allocations", "Monte Carlo"])

with tab1:
    st.header("Price Series")
    fig, ax = plt.subplots(figsize=(10, 5))
    data_to_plot = prices / prices.iloc[0] if normalize else prices
    for col in data_to_plot.columns:
        ax.plot(data_to_plot.index, data_to_plot[col], label=col)
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized Price" if normalize else "Price")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

with tab2:
    st.header("Optimal Portfolio Allocations")
    if allow_shorts:
        # Grouped bar chart for allocations when shorts allowed
        fig, ax = plt.subplots(figsize=(8, 4))
        weights_df.plot.bar(ax=ax)
        ax.set_title("Portfolio Weights: Min Variance vs Max Sharpe")
        ax.set_ylabel("Weight")
        ax.grid(True, axis="y")
        st.pyplot(fig)
    else:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        weights_df.iloc[:, 0].plot(kind="pie", ax=axes[0], autopct="%.1f%%", startangle=90)
        axes[0].set_title("Min Variance")
        axes[0].set_ylabel("")
        weights_df.iloc[:, 1].plot(kind="pie", ax=axes[1], autopct="%.1f%%", startangle=90)
        axes[1].set_title("Max Sharpe")
        axes[1].set_ylabel("")
        st.pyplot(fig)

with tab3:
    st.header("Monte Carlo Simulation")
    mc_n = num_portfolios
    mc = np.zeros((mc_n, 2))
    for i in range(mc_n):
        if allow_shorts:
            w = np.random.randn(len(ann_returns))
            w /= np.sum(w)
        else:
            w = np.random.rand(len(ann_returns))
            w /= np.sum(w)
        mc[i, 0] = np.sqrt(w.dot(ann_cov.values).dot(w))
        mc[i, 1] = w.dot(ann_returns.values)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(mc[:, 0], mc[:, 1], color='gray', alpha=0.5)
    ax.scatter([vol_mvp], [ret_mvp], color='red', marker='*', s=200, label='Min Variance')
    ax.scatter([vol_tan], [ret_tan], color='blue', marker='*', s=200, label='Max Sharpe')
    ax.set_xlabel('Volatility')
    ax.set_ylabel('Return')
    ax.set_title(f'Monte Carlo Portfolios (n={mc_n})')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)