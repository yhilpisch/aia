# Management Report: Analysis of EOD Stock Data and Pairs Trading Strategy Backtest

**Date:** May 28, 2025

-----

### I. Executive Summary

This report provides a comprehensive analysis of End-of-Day (EOD) stock data for 14 major companies from May 2015 to May 2025. The analysis covers overall market trends, individual stock performance, volatility, and inter-stock correlations. A significant portion of the report is dedicated to identifying potential pairs for a statistical pairs trading strategy using cointegration tests and subsequently backtesting this strategy.

Key findings indicate a strong bull market for technology stocks over the analyzed decade, with NVIDIA (NVDA) and AMD leading in total returns. While many stocks exhibit strong correlations, only a few pairs demonstrated statistically significant cointegration, suggesting a long-term mean-reverting relationship suitable for pairs trading. A simplified backtest of the top three cointegrated pairs (META-JPM, MSFT-GOOG, INTC-GE) yielded positive but modest returns, highlighting the need for further optimization and consideration of real-world trading costs.

-----

### II. Data Overview

The dataset comprises 2533 daily entries for 14 stocks, covering the period from May 1, 2015, to May 1, 2025. All stock prices are recorded as floating-point numbers, and there are no missing values, ensuring data completeness for analysis.

| Date       | AAPL    | MSFT    | AMZN    | NFLX    | META    | GOOG    | INTC    | AMD   | NVDA   | GE      | GS      | BAC     | JPM     | MS      |
|:-----------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|:------|:-------|:-------|:--------|:--------|:--------|:--------|
| 2015-05-01 | 28.7604 | 41.9202 | 21.1435 | 79.5756 | 78.6195 | 26.7682 | 25.8267 | 2.31  | 0.5481 | 113.25  | 161.814 | 13.036  | 48.3388 | 28.3858 |
| 2015-05-04 | 28.7046 | 41.5584 | 21.152  | 79.2713 | 78.4403 | 26.9115 | 25.8344 | 2.31  | 0.5448 | 113.084 | 163.264 | 13.303  | 49.1823 | 28.6885 |
| 2015-05-05 | 28.0578 | 41.007  | 21.0595 | 80.7928 | 77.1962 | 26.4149 | 25.4063 | 2.28  | 0.5308 | 111.633 | 161.618 | 13.2302 | 48.9391 | 28.3404 |
| 2015-05-06 | 27.8816 | 39.8698 | 20.955  | 80.077  | 77.7336 | 26.0874 | 25.0794 | 2.29  | 0.5325 | 111.176 | 160.766 | 13.1817 | 48.5743 | 28.0377 |
| 2015-05-07 | 28.0541 | 40.2317 | 21.344  | 80.7485 | 78.0571 | 26.4099 | 25.0988 | 2.32  | 0.5419 | 112.13  | 161.7   | 13.1412 | 49.0151 | 28.4085 |

**Descriptive Statistics:**

|       | AAPL    | MSFT    | AMZN    | NFLX    | META    | GOOG    | INTC    | AMD     | NVDA    | GE      | GS      | BAC     | JPM     | MS      |
|:------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|
| count | 2533    | 2533    | 2533    | 2533    | 2533    | 2533    | 2533    | 2533    | 2533    | 2533    | 2533    | 2533    | 2533    | 2533    |
| mean  | 101.139 | 194.811 | 108.026 | 370.613 | 241.378 | 87.8063 | 36.7957 | 62.2236 | 25.4035 | 89.3018 | 264.22  | 27.009  | 112.816 | 57.82   |
| std   | 68.6184 | 127.667 | 55.5963 | 222.776 | 140.831 | 46.533  | 10.3531 | 51.9785 | 37.557  | 45.775  | 119.196 | 9.24193 | 51.7833 | 29.2705 |
| min   | 20.6475 | 35.3226 | 20.955  | 79.2713 | 77.0966 | 25.7197 | 18.13   | 1.62    | 0.4674  | 26.7417 | 116.407 | 9.1124  | 41.1599 | 16.652  |
| 25%   | 37.359  | 76.172  | 55.5425 | 185.2   | 144.788 | 49.9912 | 28.0994 | 12.64   | 3.8487  | 52.9437 | 176.346 | 20.6869 | 77.8445 | 34.5953 |
| 50%   | 77.4958 | 175.445 | 97.83   | 346.19  | 187.198 | 71.3734 | 37.0558 | 53.5    | 7.8345  | 68.6777 | 209.25  | 26.1837 | 97.8801 | 43.497  |
| 75%   | 161.26  | 290.638 | 158.756 | 499.1   | 301.399 | 128.964 | 45.052  | 101.86  | 24.4449 | 126.459 | 329.255 | 33.7139 | 138.486 | 81.396  |
| max   | 258.397 | 464.002 | 242.06  | 1211.57 | 736.015 | 207.474 | 62.0851 | 211.38  | 149.416 | 241.78  | 668.873 | 47.4406 | 278.236 | 139.957 |

-----

### III. Market Performance and Trends

The period from 2015 to 2025 was marked by significant growth, particularly in the technology sector.

**Overall Stock Price Trends:**

The chart below illustrates the general upward trajectory of major tech stocks (AAPL, MSFT, AMZN, NFLX, GOOG, NVDA), contrasting with more muted or varied performance from traditional sectors (e.g., financials like BAC, GS).

**Relative Stock Performance (Normalized Prices):**

Normalizing prices to a base of 100 on the first day reveals the true growth story. NVIDIA (NVDA) stands out with an astounding increase, followed by AMD, NFLX, MSFT, and AMZN. This highlights the dominance of these tech innovators over the past decade. In contrast, Intel (INTC) notably delivered negative returns.

**Total Returns (%) for Each Stock:**

|      | 0       |
|:-----|:--------|
| NVDA | 24621.8 |
| AMD  | 4859.31 |
| NFLX | 1422.54 |
| MSFT | 998.969 |
| AMZN | 874.389 |
| GOOG | 674.398 |
| AAPL | 796.401 |
| JPM  | 475.545 |
| META | 355.856 |
| MS   | 355.192 |
| GS   | 280.516 |
| BAC  | 239.214 |
| GE   | 113.492 |
| INTC | -20.4312 |

-----

### IV. Volatility Analysis

Volatility, measured by the annualized 30-day rolling standard deviation of daily returns, indicates the degree of price fluctuations. High-growth tech stocks such as AMD, NVDA, NFLX, and META exhibit higher volatility, reflecting their higher risk-reward profiles.

**Daily Returns Descriptive Statistics:**

|       | AAPL        | MSFT        | AMZN       | NFLX        | META        | GOOG        | INTC        | AMD         | NVDA       | GE          | GS          | BAC         | JPM         | MS          |
|:------|:------------|:------------|:-----------|:------------|:------------|:------------|:------------|:------------|:-----------|:------------|:------------|:------------|:------------|:------------|
| count | 2532        | 2532        | 2532       | 2532        | 2532        | 2532        | 2532        | 2532        | 2532       | 2532        | 2532        | 2532        | 2532        | 2532        |
| mean  | 0.000937212 | 0.00109352  | 0.00111312 | 0.0014516   | 0.00112345  | 0.000907048 | 0.000197364 | 0.00221631  | 0.00266999 | 0.000548931 | 0.000701752 | 0.000678893 | 0.000824557 | 0.000802177 |
| std   | 0.0184834   | 0.0171261   | 0.020698   | 0.0271786   | 0.0241122   | 0.0183307   | 0.0238693   | 0.0371368   | 0.0315065  | 0.0223318   | 0.0186609   | 0.019833    | 0.0174542   | 0.0202054   |
| min   | -0.128647   | -0.14739    | -0.140494  | -0.351166   | -0.263901   | -0.111008   | -0.260586   | -0.242291   | -0.187559  | -0.151593   | -0.127053   | -0.153974   | -0.149648   | -0.155999   |
| 25%   | -0.0074522  | -0.00686182 | -0.0088439 | -0.011367   | -0.00926632 | -0.0072459  | -0.0103175  | -0.0169506  | -0.0130213 | -0.00939967 | -0.00840525 | -0.00914307 | -0.00711238 | -0.0088793  |
| 50%   | 0.000894966 | 0.000980108 | 0.00112611 | 0.000610483 | 0.00109049  | 0.00117433  | 0.000562516 | 0.000575114 | 0.00262172 | 0           | 0.000564165 | 0.000447809 | 0.000614274 | 0.000784812 |
| 75%   | 0.0101411   | 0.00982943  | 0.0115868  | 0.0144418   | 0.0124591   | 0.00984888  | 0.0113469   | 0.0204483   | 0.0181366  | 0.0103048   | 0.0102604   | 0.0105136   | 0.00891547  | 0.0110975   |
| max   | 0.153289    | 0.142168    | 0.135359   | 0.190281    | 0.232824    | 0.160526    | 0.195213    | 0.522901    | 0.298098   | 0.1473      | 0.175803    | 0.177964    | 0.180125    | 0.197698    |

-----

### V. Correlation Analysis

The correlation matrix of stock prices reveals strong positive correlations within specific sectors (e.g., tech stocks like AAPL, MSFT, AMZN, GOOG, META, NVDA, AMD moving together) and within the financial sector (GS, BAC, JPM, MS). This suggests that market-wide movements significantly influence these stocks. Understanding these correlations is vital for portfolio diversification and identifying potential pairs for trading strategies.

-----

### VI. Pairs Trading Strategy Analysis

A pairs trading strategy exploits the mean-reverting property of the spread between two cointegrated stocks.

#### A. Cointegration Test Results

Cointegration implies a long-term, stable relationship between stock prices, where their linear combination tends to revert to a mean. The Engle-Granger two-step cointegration test was performed on all possible pairs. A p-value below 0.05 is typically considered statistically significant for cointegration.

**Cointegration Test Results (Ranked by P-value):**

| Pair        | P-value   |
|:------------|:----------|
| META - JPM  | 0.019661  |
| MSFT - GOOG | 0.0281565 |
| INTC - GE   | 0.0477599 |
| AAPL - GOOG | 0.0548108 |
| GOOG - BAC  | 0.077629  |
| ...         | ...       |
| NFLX - INTC | 1         |
| NFLX - AMD  | 1         |

**Pairs with Cointegration P-value \< 0.05 (Potentially Cointegrated):**

Based on a 0.05 significance level, the following pairs show statistical evidence of cointegration:

  * **META - JPM** (P-value: 0.019661)
  * **MSFT - GOOG** (P-value: 0.0281565)
  * **INTC - GE** (P-value: 0.0477599)

These pairs are promising candidates for a pairs trading strategy, as their price relationships exhibit mean-reverting tendencies.

#### B. Backtesting Results

A simplified pairs trading strategy was backtested for the top three cointegrated pairs. The strategy involves:

  * Calculating a dynamic hedge ratio using OLS regression.
  * Standardizing the spread into a Z-score (60-day rolling window).
  * Entering trades when the Z-score exceeds +/- 2 standard deviations.
  * Exiting trades when the Z-score reverts to +/- 0.5 standard deviations.
  * Initial capital: $100,000.

**Pair: META and JPM**

  * Calculated Hedge Ratio (META vs JPM): 2.5566
  * Total Trades: 42
  * Cumulative P\&L: $266.18
  * Final Capital: $100,266.18
  * Return on Capital: 0.27%

**Pair: MSFT and GOOG**

  * Calculated Hedge Ratio (MSFT vs GOOG): 2.6881
  * Total Trades: 51
  * Cumulative P\&L: $190.67
  * Final Capital: $100,190.67
  * Return on Capital: 0.19%

**Pair: INTC and GE**

  * Calculated Hedge Ratio (INTC vs GE): -0.1600
  * Total Trades: 49
  * Cumulative P\&L: $56.31
  * Final Capital: $100,056.31
  * Return on Capital: 0.06%

#### C. Backtest Performance Summary

The backtest results indicate that the pairs trading strategy, with the defined parameters, generated positive but relatively modest returns across all three tested pairs. While the number of trades was significant for each pair, the overall profit per trade appears to be low. The return on initial capital is minimal (ranging from 0.06% to 0.27%), suggesting that transaction costs (not included in this simplified model) could easily negate these profits in a live trading environment.

-----

### VII. Conclusion and Recommendations

The analysis confirms the robust growth of the tech sector over the last decade and highlights significant differences in performance and volatility among the stocks. While strong correlations are common, cointegration is a rarer and more critical property for statistical arbitrage strategies like pairs trading.

**Key Findings:**

  * NVIDIA and AMD were exceptional performers, showcasing immense growth.
  * Intel significantly underperformed the market.
  * The pairs META-JPM, MSFT-GOOG, and INTC-GE were identified as statistically cointegrated.
  * The basic backtest yielded marginal positive returns, implying that the strategy, as implemented, may not be highly profitable without further refinement.

**Recommendations:**

1.  **Parameter Optimization:** Conduct extensive research and optimization of backtesting parameters (rolling window size, entry/exit thresholds) to potentially maximize profitability and reduce drawdowns.
2.  **Transaction Costs & Slippage:** Incorporate realistic transaction costs (commissions, bid-ask spread, slippage) into the backtest to assess true profitability.
3.  **Risk Management:** Implement robust risk management techniques, including position sizing, stop-loss mechanisms, and diversification across multiple pairs.
4.  **Dynamic Hedge Ratio:** Explore more advanced methods for calculating the hedge ratio, such as Kalman filters, which allow the hedge ratio to change over time, potentially capturing dynamic relationships better.
5.  **Robustness Testing:** Test the strategy across different market regimes and time periods to ensure its robustness and resilience.
6.  **Alternative Cointegration Tests:** Investigate other cointegration tests (e.g., Johansen test for multiple series) to validate the relationships.
7.  **Fundamental Analysis:** Combine statistical analysis with fundamental insights to understand why certain pairs are cointegrated and if that relationship is likely to persist.

While pairs trading can be a viable strategy, its success heavily relies on rigorous statistical analysis, careful parameter tuning, and a comprehensive understanding of market microstructure and trading costs. The current analysis provides a solid foundation for further exploration into this area.