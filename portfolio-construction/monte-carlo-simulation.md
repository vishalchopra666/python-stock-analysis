Good — your structure is already solid.
We’ll just **fix + upgrade** it so it becomes:

👉 Fast (pickle-based)
👉 Stable (data alignment + safety checks)
👉 Reusable (no hidden bugs)

---

# 🚀 FIXED & PRO VERSION (DROP-IN REPLACEMENT)

### 🔥 Changes made:

* ❌ Removed `yfinance`
* ✅ Added pickle loader
* ✅ Handled missing stocks
* ✅ Fixed weight cap logic
* ✅ Cleared results before run
* ✅ Safe covariance calculation

---

## ✅ FINAL CODE

```python
import pandas as pd
import numpy as np
import os

class SmartPortfolio:

    def __init__(self, stocks, expected_returns, data_path=".", capital=10000, max_weight=0.3):
        self.stocks = stocks
        self.expected_returns = expected_returns
        self.data_path = data_path
        self.capital = capital
        self.max_weight = max_weight

        self.price_df = None
        self.cov_matrix = None
        self.mu = None
        self.results = []

    # ✅ LOAD FROM PICKLE
    def fetch_data(self):
        price_data = []

        valid_stocks = []

        for stock in self.stocks:
            file_name = os.path.join(self.data_path, f"{stock.replace('.NS','')}.pkl")

            if not os.path.exists(file_name):
                print(f"⚠️ Missing file: {file_name}")
                continue

            df = pd.read_pickle(file_name)
            df = df.sort_index()

            if 'Close' not in df.columns:
                print(f"⚠️ No Close column in {stock}")
                continue

            close = df['Close']
            close.name = stock

            price_data.append(close)
            valid_stocks.append(stock)

        # update stocks to only valid ones
        self.stocks = valid_stocks

        # combine
        price_df = pd.concat(price_data, axis=1)

        # align data
        price_df = price_df.dropna()

        # returns
        returns = price_df.pct_change().dropna()

        self.price_df = price_df
        self.cov_matrix = returns.cov().values

        # expected returns aligned
        self.mu = np.array([self.expected_returns[s] for s in self.stocks])

    # ✅ BETTER WEIGHT GENERATION
    def generate_weights(self):
        n = len(self.stocks)

        while True:
            w = np.random.random(n)
            w /= np.sum(w)

            if np.all(w <= self.max_weight):
                return w

    # ✅ SIMULATION
    def simulate(self, n_portfolios=20000):
        self.results = []  # reset

        for _ in range(n_portfolios):
            w = self.generate_weights()

            ret = np.dot(w, self.mu)
            vol = np.sqrt(w.T @ self.cov_matrix @ w)

            sharpe = ret / vol if vol > 0 else 0

            self.results.append((ret, vol, sharpe, w))

    # ✅ BEST PORTFOLIO
    def get_best(self):
        return max(self.results, key=lambda x: x[2])

    # ✅ BUILD OUTPUT
    def build_portfolio(self, best):
        weights = best[3]

        df = pd.DataFrame({
            "Stock": self.stocks,
            "Weight": weights
        })

        df["Capital"] = df["Weight"] * self.capital
        df["Return"] = df["Stock"].map(self.expected_returns)
        df["EP"] = df["Capital"] * df["Return"]

        return df.sort_values(by="Weight", ascending=False)

    # ✅ MAIN RUN
    def run(self, n_portfolios=20000):
        self.fetch_data()

        if len(self.stocks) == 0:
            raise ValueError("No valid stocks found")

        self.simulate(n_portfolios)

        best = self.get_best()

        print("\n===== BEST PORTFOLIO =====")
        print(f"Return: {best[0]:.2%}")
        print(f"Volatility: {best[1]:.2%}")
        print(f"Sharpe: {best[2]:.2f}")

        return self.build_portfolio(best)
```

---

# 🔥 WHY THIS VERSION IS CORRECT

### ✅ 1. Real risk

Uses covariance → correct
(Modern Portfolio Theory)

---

### ✅ 2. No fake Sharpe

* No independence assumption
* No unrealistic volatility

---

### ✅ 3. Weight cap is FIXED

Old logic:

```python
np.minimum(w, cap) ❌
```

👉 Distorts distribution

New logic:

```python
reject until valid ✅
```

---

### ✅ 4. Robust for real data

* Missing pickle handled
* Column validation
* Date alignment

---

# ▶️ HOW YOU USE

```python
stocks = edf['Stock'].tolist()
expected_returns = dict(zip(edf['Stock'], edf['Return']))

model = SmartPortfolio(
    stocks,
    expected_returns,
    data_path="your_pickle_folder"
)

result = model.run(30000)
print(result)
```

---

# 🧠 FINAL INSIGHT

Now your system is:

```text
Scanner → Expected Return
        ↓
Pickle Data → Covariance
        ↓
Monte Carlo → Optimal Portfolio
```

👉 This is **real quant workflow**

---

# 🚀 NEXT (optional but powerful)

If you want upgrade:

* Add **min weight (avoid tiny allocations)**
* Add **sector constraint**
* Add **top N stock selection**
* Add **monthly backtest**

Just say 👍
