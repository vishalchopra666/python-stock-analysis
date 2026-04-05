Perfect — now we complete your system 🔥

You already have:

* ✅ Top-N Max Return (aggressive)
  Now we build:
* ✅ **Top-N Minimum Risk with Return Constraint (smart aggressive)**

👉 This is **best practical model** for your use.

---

# 📉 Top-N Minimum Risk with Return Constraint (Monte Carlo Portfolio)

## 🚀 Objective

```text id="0u6l0x"
From large universe (50 stocks)
→ select best N stocks (5–10)
→ ensure minimum return
→ minimize risk
```

---

# 🧠 Concept

This combines:

* Subset selection (Top-N)
* Risk control (covariance)
* Return filtering

From Modern Portfolio Theory

---

# ⚙️ Strategy Logic

```text id="h6w6ak"
1. Randomly pick N stocks
2. Assign weights
3. Calculate return & risk
4. Keep only portfolios with return ≥ target
5. Select lowest risk among them
```

---

# 📁 Inputs

```python
stocks = edf['Stock'].tolist()
expected_returns = dict(zip(edf['Stock'], edf['Return']))
```

---

# 🔥 FULL IMPLEMENTATION

```python
import pandas as pd
import numpy as np
import os
import random

class TopNMinRiskPortfolio:

    def __init__(
        self,
        stocks,
        expected_returns,
        data_path=".",
        capital=10000,
        n_select=5,
        max_weight=0.4,
        min_weight=0.05,
        min_return=0.18
    ):
        self.stocks = stocks
        self.expected_returns = expected_returns
        self.data_path = data_path
        self.capital = capital

        self.n_select = n_select
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.min_return = min_return

        self.price_df = None
        self.cov_matrix = None
        self.results = []

    # 🔹 Load ALL data once
    def fetch_data(self):
        price_data = []
        valid_stocks = []

        for stock in self.stocks:
            file = os.path.join(self.data_path, f"{stock.replace('.NS','')}.pkl")

            if not os.path.exists(file):
                continue

            df = pd.read_pickle(file).sort_index()

            if 'Close' not in df.columns:
                continue

            s = df['Close']
            s.name = stock

            price_data.append(s)
            valid_stocks.append(stock)

        self.stocks = valid_stocks

        price_df = pd.concat(price_data, axis=1, sort=False)
        price_df = price_df.ffill()

        returns = price_df.pct_change().dropna()
        returns = returns.loc[:, returns.count() > 200]

        self.price_df = price_df
        self.cov_matrix_full = returns.cov().values * 252

        self.stock_index = {s: i for i, s in enumerate(self.stocks)}

    # 🔹 Generate subset + weights
    def generate_portfolio(self):
        selected = random.sample(self.stocks, self.n_select)

        weights = np.random.random(self.n_select)
        weights /= np.sum(weights)

        if not (np.all(weights <= self.max_weight) and np.all(weights >= self.min_weight)):
            return None, None

        return selected, weights

    # 🔹 Get covariance for subset
    def get_subset_cov(self, selected):
        idx = [self.stock_index[s] for s in selected]
        return self.cov_matrix_full[np.ix_(idx, idx)]

    # 🔹 Simulation
    def simulate(self, n_portfolios=50000):
        self.results = []

        for _ in range(n_portfolios):
            selected, weights = self.generate_portfolio()

            if selected is None:
                continue

            returns = np.array([self.expected_returns[s] for s in selected])
            port_return = np.dot(weights, returns)

            # 🔥 Return filter
            if port_return < self.min_return:
                continue

            cov = self.get_subset_cov(selected)
            port_vol = np.sqrt(weights.T @ cov @ weights)

            self.results.append((port_return, port_vol, selected, weights))

    # 🔹 Select minimum risk
    def get_best(self):
        return min(self.results, key=lambda x: x[1])

    # 🔹 Build output
    def build_portfolio(self, best):
        selected = best[2]
        weights = best[3]

        df = pd.DataFrame({
            "Stock": selected,
            "Weight": weights
        })

        df["Capital"] = df["Weight"] * self.capital
        df["Return"] = df["Stock"].map(self.expected_returns)
        df["EP"] = df["Capital"] * df["Return"]

        return df.sort_values(by="Weight", ascending=False)

    # 🔹 Run
    def run(self, n_portfolios=50000):
        self.fetch_data()

        if len(self.stocks) < self.n_select:
            raise ValueError("Not enough valid stocks")

        self.simulate(n_portfolios)

        if len(self.results) == 0:
            raise ValueError("No portfolio meets return constraint")

        best = self.get_best()

        print("\n===== TOP-N MIN RISK (WITH RETURN FILTER) =====")
        print(f"Return: {best[0]:.2%}")
        print(f"Volatility: {best[1]:.2%}")

        return self.build_portfolio(best)
```

---

# ▶️ Usage

```python
model = TopNMinRiskPortfolio(
    stocks,
    expected_returns,
    data_path="your_pickle_folder",
    n_select=5,
    min_return=0.18
)

result = model.run(50000)
print(result)
```

---

# 🎯 Parameter Guide

| Parameter  | Meaning                    |
| ---------- | -------------------------- |
| n_select   | Number of stocks (5 or 10) |
| min_return | Profit filter              |
| max_weight | Avoid concentration        |
| min_weight | Avoid tiny allocation      |

---

# 🧠 Strategy Insight

```text id="t9b3ay"
Pick few stocks
→ ensure good return
→ choose safest combination
```

---

# 📊 Compared to other models

| Model            | Behavior           |
| ---------------- | ------------------ |
| Top-N Max Return | Very aggressive    |
| Max Sharpe       | Balanced           |
| Min Risk         | Defensive          |
| THIS MODEL       | Smart aggressive ✅ |

---

# ⚠️ Notes

* Needs more simulations (50k+)
* Works best with good stock selection (your scanner)
* Still requires manual validation

---

# 🏁 Final Summary

```text id="z3u3bb"
50 stocks
   ↓
Pick N stocks
   ↓
Filter high return
   ↓
Select lowest risk
   ↓
Final portfolio
```

👉 This is closest to **real-world portfolio building**

---

---

# 🔥 You now have full system

* Aggressive → Top-N max return
* Balanced → Sharpe
* Safe → Min risk
* Smart aggressive → THIS model

---

If you want next:

👉 I can unify all into **single class with modes**
That becomes a full product 🚀
