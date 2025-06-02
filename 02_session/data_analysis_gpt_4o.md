# 📊 Statistical Pairs Trading Analysis Report

## 1. Overview

This report investigates statistical relationships between major U.S. stocks from May 2015 to 2025 using cointegration analysis and backtesting of pairs trading strategies. The analysis covers:

* Cointegration screening across all stock pairs
* Spread visualization of top cointegrated pairs
* A z-score-based backtest strategy
* Key recommendations for implementation

---

## 2. Data Summary

* **Number of Trading Days**: 2,533
* **Number of Stocks Analyzed**: 14
* **Sectors Covered**: Primarily Tech and Finance
* **Source**: End-of-day (EOD) adjusted closing prices

---

## 3. Price Evolution

The following chart illustrates long-term trends in selected tech stocks:

📈 *Selected Tech Stocks: AAPL, MSFT, AMZN, GOOG, NVDA*

*(Note: Include the generated line chart here in your rendered version)*

---

## 4. Correlation Analysis

Daily return correlations reveal strong clustering among tech stocks, supporting diversification between tech and finance:

🧊 *Correlation Heatmap of Daily Returns*

*(Note: Include the heatmap visualization here)*

---

## 5. Cointegration Testing

The Engle-Granger test was applied to all 91 possible stock pairs. Below are the top-ranked results:

| Rank | Pair        | P-Value | Interpretation                       |
| ---- | ----------- | ------- | ------------------------------------ |
| 1    | META & JPM  | 0.0197  | Strong signal, cross-sector pair     |
| 2    | MSFT & GOOG | 0.0282  | Strong, logical tech pair            |
| 3    | INTC & GE   | 0.0478  | Moderate tech-industrial correlation |

These pairs exhibit statistically significant mean-reverting relationships in price.

---

## 6. Spread-Based Strategy and Backtesting

### Strategy Logic

* **Enter Long** when z-score of spread < -1.0
* **Enter Short** when z-score > +1.0
* **Exit** when spread reverts toward 0

### Cumulative PnL Results

📉 *Backtest PnL: MSFT-GOOG vs. META-JPM*

*(Note: Include the cumulative PnL line chart here)*

**Observations:**

* **MSFT-GOOG** produced smoother returns and better performance — a clear candidate for deployment.
* **META-JPM**, despite strong cointegration, shows higher volatility and sectoral mismatch.

---

## 7. Recommendations

1. **Prioritize MSFT-GOOG** for production strategies due to its stability and sector alignment.
2. **Use rolling hedge ratios and z-score thresholds** for more adaptive strategies.
3. **Incorporate transaction cost models** and position sizing rules to assess real-world feasibility.
4. **Expand analysis using ML techniques** for pair selection, anomaly detection, and signal timing.

---

## 8. Next Steps

Would you like to:

* Add rolling regression or OU modeling?
* Simulate real capital allocation and Sharpe ratio analysis?
* Generate a dashboard for live spread monitoring?

Let me know how you'd like to proceed. I can deliver the next phase as code, notebook, or LaTeX.
