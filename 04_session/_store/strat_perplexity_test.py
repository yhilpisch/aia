import pandas as pd
import matplotlib.pyplot as plt

# Load the price data
df = pd.read_csv('aia_eod_data.csv', index_col='Date', parse_dates=True)

# Define long and short portfolios
longs = ['NVDA', 'AAPL', 'META']
shorts = ['NFLX', 'MS', 'INTC']

# Calculate daily returns
returns = df[longs + shorts].pct_change().dropna()

# Compute portfolio daily returns: equally weighted long-short
portfolio_returns = returns[longs].mean(axis=1) - returns[shorts].mean(axis=1)

# Calculate cumulative returns
cumulative_returns = (1 + portfolio_returns).cumprod()

# Plot the cumulative return
plt.figure(figsize=(12, 6))
plt.plot(cumulative_returns.index, cumulative_returns.values, label='Long-Short Portfolio')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.title('Long-Short Portfolio Cumulative Return Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
