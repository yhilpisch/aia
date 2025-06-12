import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load CSV
data = pd.read_csv('aia_eod_data.csv', parse_dates=['Date'], index_col='Date')

# Select relevant tickers
tickers = ['NVDA', 'JPM', 'GE', 'MS']
prices = data[tickers]

# Filter last 3 years from last available date
end_date = prices.index.max()
start_date = end_date - pd.DateOffset(years=3)
prices = prices.loc[start_date:end_date]

# Calculate daily returns
returns = prices.pct_change().dropna()

# Portfolio weights
weights = {'NVDA': 0.25, 'JPM': 0.25, 'GE': -0.25, 'MS': -0.25}

# Calculate portfolio returns
portfolio_returns = (returns * pd.Series(weights)).sum(axis=1)

# Calculate cumulative returns
cumulative_returns = (1 + portfolio_returns).cumprod()

# Performance metrics
total_return = cumulative_returns[-1] - 1
annualized_vol = portfolio_returns.std() * np.sqrt(252)
rolling_max = cumulative_returns.cummax()
drawdown = (cumulative_returns - rolling_max) / rolling_max
max_drawdown = drawdown.min()
sharpe_ratio = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252)

# Output results
print(f'Cumulative Return: {total_return:.2%}')
print(f'Annualized Volatility: {annualized_vol:.2%}')
print(f'Max Drawdown: {max_drawdown:.2%}')
print(f'Sharpe Ratio: {sharpe_ratio:.2f}')

# Plot portfolio value
plt.figure(figsize=(12,6))
plt.plot(cumulative_returns, label='Long/Short Portfolio')
plt.title('3-Year Backtest: Long NVDA/JPM, Short GE/MS')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.legend()
plt.grid(True)
plt.show()
