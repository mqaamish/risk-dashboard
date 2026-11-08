import numpy as np
import pandas as pd
from scipy.stats import norm
from data import TICKERS

PORTFOLIO_VALUE = 1_000_000

returns = pd.read_csv("returns.csv", index_col=0, parse_dates=True)
asset_returns = returns[TICKERS]
weights = np.full(len(TICKERS), 1 / len(TICKERS))
port_returns = asset_returns @ weights

def historical_var(r, conf):
    return -np.percentile(r, (1 - conf) * 100)

def parametric_var(r, conf):
    return -(r.mean() + norm.ppf(1 - conf) * r.std())

def monte_carlo_var(asset_returns, weights, conf, n=10_000, seed=42):
    rng = np.random.default_rng(seed)
    sims = rng.multivariate_normal(
        asset_returns.mean().values, asset_returns.cov().values, size=n
    )
    port = sims @ weights
    return -np.percentile(port, (1 - conf) * 100)

if __name__ == "__main__":
    print(f"Portfolio value: ${PORTFOLIO_VALUE:,.0f} (equal weight, 1 day VaR)\n")
    for conf in (0.95, 0.99):
        h = historical_var(port_returns, conf)
        p = parametric_var(port_returns, conf)
        m = monte_carlo_var(asset_returns, weights, conf)
        print(f"{int(conf*100)}% confidence")
        print(f"  Historical : {h:.2%}  (${h*PORTFOLIO_VALUE:,.0f})")
        print(f"  Parametric : {p:.2%}  (${p*PORTFOLIO_VALUE:,.0f})")
        print(f"  Monte Carlo: {m:.2%}  (${m*PORTFOLIO_VALUE:,.0f})\n")