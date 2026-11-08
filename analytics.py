import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data import TICKERS, BENCHMARK

returns = pd.read_csv("returns.csv", index_col=0, parse_dates=True)
asset_returns = returns[TICKERS]
bench = returns[BENCHMARK]
weights = np.full(len(TICKERS), 1 / len(TICKERS))
port_returns = asset_returns @ weights

def betas(asset_returns, bench):
    return asset_returns.apply(lambda s: s.cov(bench) / bench.var())

def rolling_vol(r, window=30):
    return r.rolling(window).std() * np.sqrt(252)

def max_drawdown(r):
    cum = (1 + r).cumprod()
    dd = cum / cum.cummax() - 1
    return dd.min(), dd

if __name__ == "__main__":
    corr = asset_returns.corr()
    mask = np.triu(np.ones(corr.shape), k=1).astype(bool)
    pairs = corr.where(mask).stack().sort_values(ascending=False)
    print("Most correlated pairs:")
    print(pairs.head(3).round(2))
    print(f"Average pairwise correlation: {pairs.mean():.2f}\n")

    b = betas(asset_returns, bench)
    print(f"Portfolio beta vs {BENCHMARK}: {(b.values @ weights):.2f}")
    print("Highest beta stocks:")
    print(b.sort_values(ascending=False).head(3).round(2))
    print()

    vol = rolling_vol(port_returns)
    print(f"Annualized volatility, latest 30 day: {vol.iloc[-1]:.1%}")
    print(f"Annualized volatility, average: {vol.mean():.1%}")

    mdd, dd = max_drawdown(port_returns)
    print(f"Max drawdown: {mdd:.1%} (on {dd.idxmin().date()})")

    plt.figure(figsize=(9, 7))
    plt.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar()
    plt.xticks(range(len(TICKERS)), TICKERS, rotation=90)
    plt.yticks(range(len(TICKERS)), TICKERS)
    plt.title("Correlation matrix")
    plt.tight_layout()
    plt.savefig("correlation.png")
    plt.close()

    vol.plot(title="Rolling 30 day volatility (annualized)", figsize=(9, 4))
    plt.tight_layout()
    plt.savefig("volatility.png")
    plt.close()

    dd.plot(title="Portfolio drawdown", figsize=(9, 4))
    plt.tight_layout()
    plt.savefig("drawdown.png")
    plt.close()
    print("\nSaved: correlation.png, volatility.png, drawdown.png")