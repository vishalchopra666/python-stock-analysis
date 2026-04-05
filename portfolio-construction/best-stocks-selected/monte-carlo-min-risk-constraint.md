Perfect — this is the **right model for your goal** 👍
Let’s finalize a clean, **evergreen version** you can directly use/save.

---

# 📉 Minimum Risk with Return Constraint (Monte Carlo Portfolio)

## 🚀 Objective

```text
Maximize profit (filtered) 
while minimizing risk
```

👉 Practical meaning:

```text
Reject low-return portfolios
→ Among remaining → pick lowest volatility
```

---

# 🧠 Concept

From Modern Portfolio Theory:

```text
No free lunch:
Higher return → higher risk
```

So we enforce:

```text
Return ≥ target
AND
Risk → minimum
```

---

# 📁 Inputs

```python
stocks = edf['Stock'].tolist()

expected_returns = dict(zip(edf['Stock'], edf['Return']))
```

Data:

* Pickle OHLC files
* Must contain `Close`

---

# ⚙️ FINAL PRODUCTION CODE

```python
import pandas as pd
import numpy as np
import os

class MinRiskPortfolio:

    def __init__(
        self,
        stocks,
        expected_returns,
        data_path=".",
        capital=10000,
        max_weight=0.3,
        min_weight=0.05,
        min_return=0.18
    ):
        self.stocks = stocks
        self.expected_returns = expected_returns
        self.data_path = data_path
        self.capital = capital

        self.max_weight = max_weight
        self.min_weight = min_weight
        self.min_return = min_return

        self.price_df = None
        self.cov_matrix = None
        self.mu = None
        self.results = []

    # 🔹 Load data from pickle
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

        # Remove weak data stocks
        returns = returns.loc[:, returns.count() > 200]

        self.price_df = price_df

        # Annualized covariance
        self.cov_matrix = returns.cov().values * 252

        # Align expected returns
        self.mu = np.array([self.expected_returns[s] for s in self.stocks])

    # 🔹 Generate valid weights
    def generate_weights(self):
        n = len(self.mu)

        while True:
            w = np.random.random(n)
            w /= np.sum(w)

            if np.all(w <= self.max_weight) and np.all(w >= self.min_weight):
                return w

    # 🔹 Monte Carlo Simulation
    def simulate(self, n_portfolios=30000):
        self.results = []

        for _ in range(n_portfolios):
            w = self.generate_weights()

            ret = np.dot(w, self.mu)
            vol = np.sqrt(w.T @ self.cov_matrix @ w)

            # 🔥 KEY CONDITION
            if ret >= self.min_return:
                self.results.append((ret, vol, w))

    # 🔹 Select minimum risk
    def get_best(self):
        return min(self.results, key=lambda x: x[1])

    # 🔹 Build portfolio
    def build_portfolio(self, best):
        weights = best[2]

        df = pd.DataFrame({
            "Stock": self.stocks,
            "Weight": weights
        })

        df["Capital"] = df["Weight"] * self.capital
        df["Return"] = df["Stock"].map(self.expected_returns)
        df["EP"] = df["Capital"] * df["Return"]

        return df.sort_values(by="Weight", ascending=False)

    # 🔹 Run full pipeline
    def run(self, n_portfolios=30000):
        self.fetch_data()

        if len(self.stocks) == 0:
            raise ValueError("No valid stocks")

        self.simulate(n_portfolios)

        if len(self.results) == 0:
            raise ValueError("No portfolio meets return constraint")

        best = self.get_best()

        print("\n===== MIN RISK (WITH RETURN FILTER) =====")
        print(f"Return: {best[0]:.2%}")
        print(f"Volatility: {best[1]:.2%}")

        return self.build_portfolio(best)
```

---

# ▶️ Usage

```python
model = MinRiskPortfolio(
    stocks,
    expected_returns,
    data_path="your_pickle_folder",
    min_return=0.18   # 🔥 key parameter
)

result = model.run(30000)
print(result)
```

---

# 🎯 Choosing `min_return`

| Value     | Behavior   |
| --------- | ---------- |
| 0.10–0.15 | Very safe  |
| 0.15–0.20 | Balanced ✅ |
| 0.20–0.30 | Aggressive |
| >0.30     | Risky      |

---

# 🧠 Logic Summary

```text
1. Generate random portfolios
2. Filter → only high-return portfolios
3. From filtered → pick lowest risk
```

---

# 📊 What You Get

* Stable portfolio
* Controlled drawdown
* No over-aggressive allocation

---

# ⚠️ Common Pitfalls

❌ Too high `min_return` → no portfolio found
❌ Too low `min_return` → low return portfolio
❌ Ignoring covariance → wrong risk
❌ No weight cap → concentration risk

---

# 🏁 Final Strategy

```text
Filter for profit → Optimize for safety
```

👉 This is the most practical real-world approach

---

---

# 🔥 You now have the best setup

* Max Sharpe → balanced
* Min Risk + Return filter → practical (use this)

---

If you want next:

👉 I can combine both into **one switch-based system**
so you can run:

```python
mode = "safe" | "balanced" | "aggressive"
```

That’s how real tools are built 🚀
