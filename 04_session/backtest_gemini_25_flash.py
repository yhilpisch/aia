import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Part 1: Fundamental Data Analysis (for context and rationale, not directly used in backtest script logic) ---

# Load the aia_fundamentals.csv file
df_fundamentals = pd.read_csv('aia_fundamentals.csv')

# Transpose the DataFrame
df_fundamentals_transposed = df_fundamentals.set_index('Unnamed: 0').T
df_fundamentals_transposed.index.name = 'Ticker'

# Corrected list of columns to convert to numeric based on available data
numeric_cols = [
    'MarketCapitalization', 'MarketCapitalizationMln', 'EBITDA', 'PERatio',
    'PEGRatio', 'WallStreetTargetPrice', 'BookValue', 'DividendShare',
    'DividendYield', 'EarningsShare', 'EPSEstimateCurrentYear',
    'EPSEstimateNextYear', 'EPSEstimateNextQuarter',
    'EPSEstimateCurrentQuarter', 'ProfitMargin',
    'OperatingMarginTTM', 'ReturnOnAssetsTTM', 'ReturnOnEquityTTM',
    'RevenueTTM', 'RevenuePerShareTTM', 'QuarterlyRevenueGrowthYOY',
    'GrossProfitTTM', 'DilutedEpsTTM', 'QuarterlyEarningsGrowthYOY'
]

for col in numeric_cols:
    df_fundamentals_transposed[col] = pd.to_numeric(df_fundamentals_transposed[col], errors='coerce')

# (The detailed print statements for fundamental analysis are omitted here to keep the final script concise,
# as the user specifically asked for the "complete Python code for the new portfolio and the benchmarking".
# These were used in previous steps to inform portfolio selection.)

# --- Part 2: Portfolio Construction (as decided in the previous step) ---
# Long Positions: MSFT, NVDA, GOOG
# Short Positions: INTC, GE, MS

# --- Part 3: Backtest Implementation ---

# Load the EOD data
df_eod_data = pd.read_csv('aia_eod_data.csv')

# Load SPY prices for benchmark
df_spy_prices = pd.read_csv('aia_spy_prices.csv')

# Convert 'Date' columns to datetime and set as index
df_eod_data['Date'] = pd.to_datetime(df_eod_data['Date'])
df_eod_data = df_eod_data.set_index('Date').sort_index()

df_spy_prices['Date'] = pd.to_datetime(df_spy_prices['Date'])
df_spy_prices = df_spy_prices.set_index('Date').sort_index()

# Define the NEW long and short portfolio stocks
long_stocks_new = ['MSFT', 'NVDA', 'GOOG']
short_stocks_new = ['INTC', 'GE', 'MS']
all_portfolio_stocks_new = long_stocks_new + short_stocks_new

# Select only the relevant stock columns from EOD data and SPY 'SPY.US' price
df_portfolio_prices_new = df_eod_data[all_portfolio_stocks_new]
df_spy_close_new = df_spy_prices['SPY.US'].rename('SPY')

# Combine portfolio prices and SPY prices for date alignment and calculations
df_combined_prices_new = pd.concat([df_portfolio_prices_new, df_spy_close_new], axis=1)

# Drop rows with any missing values, as prices must be present for return calculations
df_combined_prices_new.dropna(inplace=True)

# Calculate daily returns for all stocks and SPY
df_daily_returns_new = df_combined_prices_new.pct_change().dropna()

# Define weights for the NEW portfolio
# Assuming equal weights for simplicity and a dollar-neutral portfolio
long_weight_new = 1 / len(long_stocks_new)
short_weight_new = -1 / len(short_stocks_new) # Negative for short positions

weights_new = {}
for stock in long_stocks_new:
    weights_new[stock] = long_weight_new
for stock in short_stocks_new:
    weights_new[stock] = short_weight_new

# Convert weights to a pandas Series for easy multiplication with returns
weights_series_new = pd.Series(weights_new)

# Calculate portfolio daily returns
portfolio_daily_returns_new = df_daily_returns_new[weights_series_new.index].dot(weights_series_new)

# --- Performance Metrics Calculation ---

# Cumulative Returns
cumulative_portfolio_returns_new = (1 + portfolio_daily_returns_new).cumprod() - 1
cumulative_spy_returns_new = (1 + df_daily_returns_new['SPY']).cumprod() - 1

# Total Returns (simply the last value of cumulative returns)
total_returns_portfolio_new = cumulative_portfolio_returns_new.iloc[-1]
total_returns_spy_new = cumulative_spy_returns_new.iloc[-1]

# Max Drawdown function
def calculate_max_drawdown(returns_series):
    cumulative_returns = (1 + returns_series).cumprod()
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns / peak) - 1
    return drawdown.min()

max_drawdown_portfolio_new = calculate_max_drawdown(portfolio_daily_returns_new)
max_drawdown_spy_new = calculate_max_drawdown(df_daily_returns_new['SPY'])

# Annualized Volatility (assuming 252 trading days in a year)
annualized_volatility_portfolio_new = portfolio_daily_returns_new.std() * np.sqrt(252)
annualized_volatility_spy_new = df_daily_returns_new['SPY'].std() * np.sqrt(252)

# Annualized Returns
annualized_returns_portfolio_new = (1 + portfolio_daily_returns_new).prod()**(252/len(portfolio_daily_returns_new)) - 1
annualized_returns_spy_new = (1 + df_daily_returns_new['SPY']).prod()**(252/len(df_daily_returns_new['SPY'])) - 1

# Sharpe Ratio (assuming risk-free rate = 0 for simplicity)
risk_free_rate = 0
sharpe_ratio_portfolio_new = (annualized_returns_portfolio_new - risk_free_rate) / annualized_volatility_portfolio_new
sharpe_ratio_spy_new = (annualized_returns_spy_new - risk_free_rate) / annualized_volatility_spy_new

# Beta and Alpha (relative to SPY)
X_new = df_daily_returns_new['SPY']
Y_new = portfolio_daily_returns_new

clean_data_new = pd.concat([X_new, Y_new], axis=1).dropna()
X_clean_new = clean_data_new['SPY']
Y_clean_new = clean_data_new.iloc[:, 1]

if not X_clean_new.empty and not Y_clean_new.empty:
    beta_new = X_clean_new.cov(Y_clean_new) / X_clean_new.var()
    alpha_new = annualized_returns_portfolio_new - (risk_free_rate + beta_new * (annualized_returns_spy_new - risk_free_rate))
else:
    beta_new = np.nan
    alpha_new = np.nan

# Summary of Performance Statistics
performance_summary_new = pd.DataFrame({
    'Metric': ['Annualized Returns', 'Total Returns', 'Annualized Volatility', 'Sharpe Ratio', 'Max Drawdown', 'Beta (vs SPY)', 'Alpha (vs SPY)'],
    'New Portfolio': [
        f'{annualized_returns_portfolio_new:.2%}',
        f'{total_returns_portfolio_new:.2%}', # Added Total Returns
        f'{annualized_volatility_portfolio_new:.2%}',
        f'{sharpe_ratio_portfolio_new:.2f}',
        f'{max_drawdown_portfolio_new:.2%}',
        f'{beta_new:.2f}',
        f'{alpha_new:.2%}'
    ],
    'SPY Benchmark': [
        f'{annualized_returns_spy_new:.2%}',
        f'{total_returns_spy_new:.2%}', # Added Total Returns
        f'{annualized_volatility_spy_new:.2%}',
        f'{sharpe_ratio_spy_new:.2f}',
        f'{max_drawdown_spy_new:.2%}',
        '1.00',
        '0.00%'
    ]
})

print("\n--- NEW Portfolio Performance Statistics ---")
print(performance_summary_new.to_string(index=False))

# Plotting cumulative returns
plt.figure(figsize=(12, 6))
plt.plot(cumulative_portfolio_returns_new, label='NEW L/S Portfolio')
plt.plot(cumulative_spy_returns_new, label='SPY Benchmark')
plt.title('Cumulative Returns of NEW L/S Portfolio vs. SPY Benchmark')
plt.xlabel('Date')
plt.ylabel('Cumulative Return')
plt.legend()
plt.grid(True)
plt.show()