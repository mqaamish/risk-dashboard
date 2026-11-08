import yfinance as yf
import pandas as pd

TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
    "JPM", "BAC", "GS", "XOM", "CVX",
    "JNJ", "PFE", "UNH", "PG", "KO",
    "WMT", "HD", "CAT", "NEE", "DIS",
]
BENCHMARK = "SPY"

def get_prices(years=3):
    raw = yf.download(
        TICKERS + [BENCHMARK],
        period=f"{years}y",
        auto_adjust=True,
        progress=False,
        threads=False,
    )["Close"]
    raw = raw.dropna(how="all").ffill()
    missing = [t for t in TICKERS + [BENCHMARK]
               if t not in raw.columns or raw[t].isna().all()]
    if missing:
        raise ValueError(f"No data for: {missing}")
    return raw

if __name__ == "__main__":
    prices = get_prices()
    returns = prices.pct_change().dropna()
    prices.to_csv("prices.csv")
    returns.to_csv("returns.csv")
    print(prices.tail())
    print(returns.describe().T[["mean", "std"]])