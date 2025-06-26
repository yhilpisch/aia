#!/usr/bin/env python3
"""
Retrieve end-of-day (EOD) stock data for multiple tickers using yfinance and plot closing prices.

Usage:
    python eod_data_visualizer.py [--tickers AAPL MSFT NFLX] [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--period PERIOD] [--normalize]
Examples:
    python eod_data_visualizer.py
    python eod_data_visualizer.py --tickers GOOG AMZN --period 6mo
    python eod_data_visualizer.py --start 2021-01-01 --end 2021-12-31
    python eod_data_visualizer.py --normalize
"""

import argparse
import datetime as dt

import matplotlib.pyplot as plt
import yfinance as yf


def parse_args():
    parser = argparse.ArgumentParser(
        description="Retrieve and plot EOD stock data for multiple tickers."
    )
    parser.add_argument(
        "-t", "--tickers",
        nargs="+",
        default=["AAPL", "MSFT", "NFLX"],
        help="List of ticker symbols (default: AAPL MSFT NFLX)",
    )
    parser.add_argument(
        "--start",
        type=str,
        default=None,
        help="Start date in YYYY-MM-DD format (default: 1 year ago if --period is not set)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="End date in YYYY-MM-DD format (default: today if --period is not set)",
    )
    parser.add_argument(
        "--period",
        type=str,
        default=None,
        help="Data period (e.g., 1y, 6mo). Overrides --start/--end when set.",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize each series to start at 1 (divide by the first closing price).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.period:
        data = yf.download(
            args.tickers,
            period=args.period,
            group_by='ticker',
        )
    else:
        end_date = args.end or dt.datetime.today().strftime("%Y-%m-%d")
        start_date = args.start or (
            dt.datetime.today() - dt.timedelta(days=365)
        ).strftime("%Y-%m-%d")
        data = yf.download(
            args.tickers,
            start=start_date,
            end=end_date,
            group_by='ticker',
        )

    plt.figure(figsize=(10, 6))
    if len(args.tickers) > 1:
        for ticker in args.tickers:
            df = data[ticker]
            series = df["Close"]
            if args.normalize:
                series = series / series.iloc[0]
            plt.plot(df.index, series, label=ticker)
    else:
        series = data["Close"]
        if args.normalize:
            series = series / series.iloc[0]
        plt.plot(data.index, series, label=args.tickers[0])

    plt.xlabel('Date')
    plt.ylabel('Closing Price (USD)')
    title = f"EOD Closing Prices for {' '.join(args.tickers)}{' (Normalized)' if args.normalize else ''}"
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main()