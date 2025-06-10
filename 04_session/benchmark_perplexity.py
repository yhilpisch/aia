import pandas as pd
import numpy as np

import warnings
warnings.simplefilter('ignore')

# Portfolio metrics from previous analysis
portfolio_metrics = {
    'Total Return': 6.125,
    'Annualized Return': 0.2158,
    'Annualized Volatility': 0.2436,
    'Sharpe Ratio': 0.89,
    'Max Drawdown': -0.3673,
    'Daily Mean Return': 0.00089,
    'Daily Volatility': 0.01534
}

# Load SPY price data
spy = pd.read_csv('aia_spy_prices.csv', parse_dates=['Date'])
spy.set_index('Date', inplace=True)

# Calculate SPY returns
spy_returns = spy['SPY.US'].pct_change().dropna()

# Calculate SPY metrics
total_return_spy = (1 + spy_returns).prod() - 1
annualized_return_spy = (1 + spy_returns.mean())**252 - 1
annualized_volatility_spy = spy_returns.std() * np.sqrt(252)
sharpe_ratio_spy = annualized_return_spy / annualized_volatility_spy if annualized_volatility_spy > 0 else np.nan

# Calculate max drawdown for SPY
cum_returns_spy = (1 + spy_returns).cumprod()
roll_max_spy = cum_returns_spy.cummax()
drawdown_spy = cum_returns_spy / roll_max_spy - 1
max_drawdown_spy = drawdown_spy.min()

# Daily mean and volatility for SPY
daily_mean_spy = spy_returns.mean()
daily_volatility_spy = spy_returns.std()

# Create comparison table
comparison_data = {
    'Metric': ['Total Return', 'Annualized Return', 'Annualized Volatility', 'Sharpe Ratio', 'Max Drawdown', 'Daily Mean Return', 'Daily Volatility'],
    'Portfolio': [portfolio_metrics['Total Return'], portfolio_metrics['Annualized Return'], portfolio_metrics['Annualized Volatility'], portfolio_metrics['Sharpe Ratio'], portfolio_metrics['Max Drawdown'], portfolio_metrics['Daily Mean Return'], portfolio_metrics['Daily Volatility']],
    'SPY ETF': [total_return_spy, annualized_return_spy, annualized_volatility_spy, sharpe_ratio_spy, max_drawdown_spy, daily_mean_spy, daily_volatility_spy]
}

comparison_df = pd.DataFrame(comparison_data)

# Format as percentage where appropriate
percentage_metrics = ['Total Return', 'Annualized Return', 'Annualized Volatility', 'Max Drawdown', 'Daily Mean Return', 'Daily Volatility']
for metric in percentage_metrics:
    comparison_df.loc[comparison_df['Metric'] == metric, ['Portfolio', 'SPY ETF']] = \
        comparison_df.loc[comparison_df['Metric'] == metric, ['Portfolio', 'SPY ETF']].map(lambda x: f'{x:.2%}')

print(comparison_df)
