Good — you spotted the real bottleneck 👍
Manual Excel prep will kill the whole system.

👉 Let’s **remove Excel dependency** and make it **auto-driven from your existing data**.

---

# 🚀 BETTER APPROACH (NO MANUAL EXCEL)

You already have:

* Seasonal returns ✔
* Stock list ✔
* Possibly price data (yfinance / pickle) ✔

👉 So we do:

```text
Your scanner → DataFrame → Optimizer
```

---

# ✅ FINAL SIMPLIFIED SYSTEM

## 🔹 Input (NO Excel)

You only pass:

```python
stocks = ["BDL", "AARTIPHARM", "ARE&M"]

expected_returns = {
    "BDL": 0.16,
    "AARTIPHARM": 0.13,
    "ARE&M": 0.07
}
```

👉 That’s it.

---

# 🧠 AUTO DATA FETCH + OPTIMIZER (FINAL CODE)

```python
import pandas as pd
import numpy as np
import yfinance as yf

class SmartPortfolio:

    def __init__(self, stocks, expected_returns, capital=10000, max_weight=0.3):
        self.stocks = stocks
        self.expected_returns = expected_returns
        self.capital = capital
        self.max_weight = max_weight

        self.price_df = None
        self.cov_matrix = None
        self.mu = None
        self.results = []

    def fetch_data(self, period="1y"):
        df = yf.download(self.stocks, period=period)["Close"]
        returns = df.pct_change().dropna()

        self.price_df = df
        self.cov_matrix = returns.cov().values
        self.mu = np.array([self.expected_returns[s] for s in self.stocks])

    def generate_weights(self):
        n = len(self.stocks)
        w = np.random.random(n)
        w /= np.sum(w)

        # Apply cap
        w = np.minimum(w, self.max_weight)
        w /= np.sum(w)

        return w

    def simulate(self, n_portfolios=20000):
        for _ in range(n_portfolios):
            w = self.generate_weights()

            ret = np.dot(w, self.mu)
            vol = np.sqrt(w.T @ self.cov_matrix @ w)
            sharpe = ret / vol if vol != 0 else 0

            self.results.append((ret, vol, sharpe, w))

    def get_best(self):
        return max(self.results, key=lambda x: x[2])

    def build_portfolio(self, best):
        weights = best[3]

        df = pd.DataFrame({
            "Stock": self.stocks,
            "Weight": weights
        })

        df["Capital"] = df["Weight"] * self.capital
        df["Return"] = df["Stock"].map(self.expected_returns)
        df["EP"] = df["Capital"] * df["Return"]

        return df

    def run(self):
        self.fetch_data()
        self.simulate()

        best = self.get_best()

        print("\n===== BEST PORTFOLIO =====")
        print(f"Return: {best[0]:.2%}")
        print(f"Volatility: {best[1]:.2%}")
        print(f"Sharpe: {best[2]:.2f}")

        return self.build_portfolio(best)
```

---

# ▶️ HOW YOU USE (SUPER SIMPLE)

```python
stocks = ["BDL.NS", "AARTIPHARM.NS", "ARE&M.NS"]

expected_returns = {
    "BDL.NS": 0.16,
    "AARTIPHARM.NS": 0.13,
    "ARE&M.NS": 0.07
}

model = SmartPortfolio(stocks, expected_returns)
result = model.run()

print(result)
```

---

# 🔥 WHY THIS IS BETTER

### ❌ Old way:

* Excel creation
* Manual updates
* Time waste

### ✅ New way:

* Direct from your scanner
* Fully automated
* Plug & play

---

# ⚡ EVEN BETTER (FOR YOU)

Since you already use pandas + pickle:

👉 Replace `fetch_data()` with your stored data:

```python
def fetch_data(self):
    df = your_combined_price_df   # from your dataset
    returns = df.pct_change().dropna()

    self.cov_matrix = returns.cov().values
    self.mu = np.array([self.expected_returns[s] for s in self.stocks])
```

---

# 🧠 FINAL ARCHITECTURE (YOUR SYSTEM)

```text
Seasonal Scanner → Expected Returns
             ↓
   Price Data (yfinance/pickle)
             ↓
     Monte Carlo Optimizer
             ↓
       Final Portfolio
```

---

# 🚀 REAL POWER MOVE (next step)

You can now:

* Run for **50–100 stocks instantly**
* Generate **monthly portfolios**
* Compare strategies
* Sell as **tool/system**

---

If you want next:

👉 “connect this with my scanner dataframe”

I’ll plug it directly into your existing workflow (zero manual work) 🔥
