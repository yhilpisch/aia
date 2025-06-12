import pandas as pd
import numpy as np
from pylab import plt

# Load the uploaded CSV file
file_path = 'aia_eod_data.csv'
price_data = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')

# Filter for the tickers in our portfolio
tickers = ['NVDA', 'JPM', 'NFLX', 'GS']
price_data = price_data[tickers].dropna()

# Define weights for long/short portfolio
weights = {'NVDA': 0.25, 'JPM': 0.25, 'NFLX': -0.25, 'GS': -0.25}

# Calculate daily returns
daily_returns = price_data.pct_change().dropna()

# Compute portfolio daily returns
portfolio_returns = daily_returns.dot([weights[t] for t in tickers])

# Compute cumulative returns
cumulative_returns = (1 + portfolio_returns).cumprod()
cumulative_df = (1 + daily_returns).cumprod()
cumulative_df['Portfolio'] = cumulative_returns

# Performance metrics
cagr = cumulative_returns[-1] ** (1 / ((cumulative_returns.index[-1] - cumulative_returns.index[0]).days / 365.25)) - 1
volatility = portfolio_returns.std() * np.sqrt(252)
sharpe_ratio = portfolio_returns.mean() / portfolio_returns.std() * np.sqrt(252)

# Plot cumulative returns
plt.figure(figsize=(12, 6))
for ticker in tickers:
    plt.plot(cumulative_df[ticker], label=ticker, linestyle='--')
plt.plot(cumulative_df['Portfolio'], label='Long/Short Portfolio', linewidth=2)
plt.title("Cumulative Returns: Long NVDA & JPM / Short NFLX & GS")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Output performance metrics
{
    'CAGR': f"{cagr:.2%}",
    'Annual Volatility': f"{volatility:.2%}",
    'Sharpe Ratio': f"{sharpe_ratio:.2f}"
}

# Restrict data to the last 3 years
three_years_ago = price_data.index.max() - pd.DateOffset(years=3)
price_data_3y = price_data[price_data.index >= three_years_ago]

# Recalculate daily returns
daily_returns_3y = price_data_3y.pct_change().dropna()

# Recalculate portfolio returns
portfolio_returns_3y = daily_returns_3y.dot([weights[t] for t in tickers])

# Recalculate cumulative returns
cumulative_returns_3y = (1 + portfolio_returns_3y).cumprod()
cumulative_df_3y = (1 + daily_returns_3y).cumprod()
cumulative_df_3y['Portfolio'] = cumulative_returns_3y

# Recalculate performance metrics
cagr_3y = cumulative_returns_3y[-1] ** (1 / ((cumulative_returns_3y.index[-1] - cumulative_returns_3y.index[0]).days / 365.25)) - 1
volatility_3y = portfolio_returns_3y.std() * np.sqrt(252)
sharpe_ratio_3y = portfolio_returns_3y.mean() / portfolio_returns_3y.std() * np.sqrt(252)

# Plot cumulative returns
plt.figure(figsize=(12, 6))
for ticker in tickers:
    plt.plot(cumulative_df_3y[ticker], label=ticker, linestyle='--')
plt.plot(cumulative_df_3y['Portfolio'], label='Long/Short Portfolio', linewidth=2)
plt.title("3-Year Cumulative Returns: Long NVDA & JPM / Short NFLX & GS")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Output performance metrics for the 3-year period
{
    '3-Year CAGR': f"{cagr_3y:.2%}",
    '3-Year Annual Volatility': f"{volatility_3y:.2%}",
    '3-Year Sharpe Ratio': f"{sharpe_ratio_3y:.2f}"
}


