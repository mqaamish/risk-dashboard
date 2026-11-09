import os
import datetime
import boto3
import yfinance as yf

BUCKET = os.environ.get("BUCKET", "aamish-risk-dashboard-571431119610")
TICKERS = [
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
    "JPM", "BAC", "GS", "XOM", "CVX",
    "JNJ", "PFE", "UNH", "PG", "KO",
    "WMT", "HD", "CAT", "NEE", "DIS",
]
BENCHMARK = "SPY"

def lambda_handler(event, context):
    yf.set_tz_cache_location("/tmp/yf")
    raw = yf.download(
        TICKERS + [BENCHMARK],
        period="3y",
        auto_adjust=True,
        progress=False,
        threads=False,
    )["Close"]
    prices = raw.dropna(how="all").ffill()

    missing = [t for t in TICKERS + [BENCHMARK]
               if t not in prices.columns or prices[t].isna().all()]
    if missing:
        raise ValueError(f"No data for: {missing}")

    body = prices.to_csv().encode()
    today = datetime.date.today().isoformat()
    s3 = boto3.client("s3")
    s3.put_object(Bucket=BUCKET, Key=f"raw/prices_{today}.csv", Body=body)
    s3.put_object(Bucket=BUCKET, Key="raw/prices_latest.csv", Body=body)
    return {"rows": len(prices), "date": today}