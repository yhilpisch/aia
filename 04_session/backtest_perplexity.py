import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# --- Load Data ---

# Load price data
price_df = pd.read_csv('aia_eod_data.csv', parse_dates=['Date'])
price_df.set_index('Date', inplace=True)
price_df = price_df[['NVDA', 'MSFT', 'AMZN', 'INTC', 'GE', 'NFLX']].dropna()

# Align dates for all stocks
price_df = price_df.dropna()

# --- Portfolio Construction ---

# Define portfolio constituents
longs = ['NVDA', 'MSFT', 'AMZN']
shorts = ['INTC', 'GE', 'NFLX']

# Equal weights for each leg (dollar neutral, 3 long, 3 short)
n_long = len(longs)
n_short = len(shorts)
long_weights = np.array([1.0 / n_long] * n_long)
short_weights = np.array([-1.0 / n_short] * n_short)

# --- Compute Daily Returns ---

returns = price_df.pct_change().dropna()

# --- Compute Portfolio Returns ---

# Long leg
long_returns = returns[longs].dot(long_weights)
# Short leg
short_returns = returns[shorts].dot(short_weights)
# Total L/S portfolio
portfolio_returns = long_returns + short_returns

# --- Compute Cumulative Returns ---

cum_returns = (1 + portfolio_returns).cumprod()

# --- Compute Performance Metrics ---

def annualized_return(r, periods_per_year=252):
    return (1 + r.mean())**periods_per_year - 1

def annualized_volatility(r, periods_per_year=252):
    return r.std() * np.sqrt(periods_per_year)

def sharpe_ratio(r, risk_free=0.0, periods_per_year=252):
    ann_ret = annualized_return(r, periods_per_year)
    ann_vol = annualized_volatility(r, periods_per_year)
    return (ann_ret - risk_free) / ann_vol if ann_vol > 0 else np.nan

def max_drawdown(cum_ret):
    roll_max = cum_ret.cummax()
    dd = cum_ret / roll_max - 1
    return dd.min()

# Calculate statistics
ann_ret = annualized_return(portfolio_returns)
ann_vol = annualized_volatility(portfolio_returns)
sharpe = sharpe_ratio(portfolio_returns)
mdd = max_drawdown(cum_returns)

# --- Output Statistics ---

print("L/S Portfolio Backtest Results (May 2015 - Jun 2025)")
print(f"Total Return:      {cum_returns.iloc[-1]-1:.2%}")
print(f"Annualized Return: {ann_ret:.2%}")
print(f"Annualized Volatility: {ann_vol:.2%}")
print(f"Sharpe Ratio:      {sharpe:.2f}")
print(f"Max Drawdown:      {mdd:.2%}")
print(f"Mean Daily Return: {portfolio_returns.mean():.4%}")
print(f"Std Daily Return:  {portfolio_returns.std():.4%}")

# --- Plot Cumulative Returns ---

plt.figure(figsize=(12,6))
plt.plot(cum_returns, label='L/S Portfolio')
plt.title('Long/Short Portfolio Cumulative Returns')
plt.xlabel('Date')
plt.ylabel('Cumulative Return (Gross)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# --- Optional: Compare to S&P 500 ETF (SPY) ---

spy = pd.read_csv('aia_spy_prices.csv', parse_dates=['Date'])
spy.set_index('Date', inplace=True)
spy = spy.reindex(price_df.index).dropna()
spy_returns = spy['SPY.US'].pct_change().dropna()
spy_cum = (1 + spy_returns).cumprod()

plt.figure(figsize=(12,6))
plt.plot(cum_returns, label='L/S Portfolio')
plt.plot(spy_cum, label='SPY ETF')
plt.title('L/S Portfolio vs SPY ETF')
plt.xlabel('Date')
plt.ylabel('Cumulative Return (Gross)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
