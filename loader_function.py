import os
import csv
import io
import boto3
import psycopg2
from psycopg2.extras import execute_values

BUCKET = os.environ.get("BUCKET", "aamish-risk-dashboard-571431119610")
KEY = "raw/prices_latest.csv"

def lambda_handler(event, context):
    body = boto3.client("s3").get_object(Bucket=BUCKET, Key=KEY)["Body"].read().decode()
    reader = csv.reader(io.StringIO(body))
    header = next(reader)
    tickers = header[1:]

    rows = []
    for r in reader:
        day = r[0][:10]
        for t, v in zip(tickers, r[1:]):
            if v != "":
                rows.append((day, t, float(v)))

    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ["DB_PASSWORD"],
        port=5432,
        sslmode="require",
        connect_timeout=10,
    )
    with conn, conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS prices ("
            "price_date DATE NOT NULL, ticker TEXT NOT NULL, "
            "close NUMERIC(14,4) NOT NULL, PRIMARY KEY (price_date, ticker))"
        )
        execute_values(
            cur,
            "INSERT INTO prices (price_date, ticker, close) VALUES %s "
            "ON CONFLICT DO NOTHING",
            rows,
            page_size=2000,
        )
        cur.execute("SELECT COUNT(*) FROM prices")
        total = cur.fetchone()[0]
    conn.close()
    return {"rows_read": len(rows), "rows_in_table": total}