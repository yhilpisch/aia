
import pandas as pd
import datetime

# Assuming 'aia_eod_data.csv' is in the same directory as this script.
# If running in an environment where the file is provided in a different way (e.g., through a platform),
# you might need to adjust the file loading mechanism.
try:
    df = pd.read_csv('aia_eod_data.csv')
except FileNotFoundError:
    print("Error: 'aia_eod_data.csv' not found. Please ensure the file is in the correct directory.")
    exit()

# Convert 'Date' column to datetime objects
df['Date'] = pd.to_datetime(df['Date'])

# Set 'Date' as the index
df = df.set_index('Date')

# Define the backtesting period (last three years from a specific end date)
# Using June 12, 2025 as the end date for consistency with the analysis
end_date = datetime.date(2025, 6, 12)
start_date = end_date - datetime.timedelta(days=3 * 365) # Approximate 3 years

# Filter data for the backtesting period
portfolio_data = df[(df.index >= pd.Timestamp(start_date)) & (df.index <= pd.Timestamp(end_date))]

# Define the portfolio assets and their positions (long/short)
# Long: NVDA, JPM
# Short: NFLX, GE
# Assuming equal weight for simplicity for each position (1/4 = 0.25)
# Short positions mean negative weight
portfolio_weights = {
    'NVDA': 0.25,
    'JPM': 0.25,
    'NFLX': -0.25,
    'GE': -0.25
}

# Select only the columns needed for the portfolio
selected_assets = list(portfolio_weights.keys())
portfolio_prices = portfolio_data[selected_assets]

# Calculate daily returns for each asset
daily_returns = portfolio_prices.pct_change().dropna()

# Calculate daily portfolio returns
# Multiply each asset's return by its weight and sum them up
portfolio_daily_returns = (daily_returns * pd.Series(portfolio_weights)).sum(axis=1)

# Calculate cumulative returns
# Start with an initial value of 1 to represent the starting portfolio value
cumulative_returns = (1 + portfolio_daily_returns).cumprod()

# Print the final cumulative return
final_cumulative_return = cumulative_returns.iloc[-1]
print(f"Final Cumulative Return of the L/S portfolio: {final_cumulative_return:.2f}")

# Optional: Plotting the cumulative returns
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
cumulative_returns.plot(title='L/S Portfolio Cumulative Returns (Last 3 Years)')
plt.xlabel('Date')
plt.ylabel('Cumulative Returns')
plt.grid(True)
plt.show()
