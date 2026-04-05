Perfect. Let’s build this **once and forever usable** — clean, realistic, extendable.

👉 Goal:
**Excel → Monte Carlo → Covariance → Constraints → Output (Excel)**
No shortcuts. No fake Sharpe.

---

# 🚀 FINAL EVERGREEN PORTFOLIO ENGINE

This version includes:

* ✔ Real covariance (correlation)
* ✔ Monte Carlo simulation
* ✔ Weight constraints
* ✔ Clean OOP design
* ✔ Excel input + output
* ✔ Reusable for any strategy (seasonal, momentum, etc.)

---

# 📁 1. Excel Structure (FINAL)

### File: `portfolio_input.xlsx`

### Sheet 1: `returns`

| Date       | BDL | AARTIPHARM | ARE&M | ... |
| ---------- | --- | ---------- | ----- | --- |
| 2024-01-01 | ... | ...        | ...   | ... |

👉 Use **daily prices or returns**

---

### Sheet 2: `expected`

| Stock      | ExpectedReturn |
| ---------- | -------------- |
| BDL        | 0.16           |
| AARTIPHARM | 0.13           |

👉 Your seasonal edge goes here

---

# 🧠 2. FINAL OOP CLASS

```python
import pandas as pd
import numpy as np

class MonteCarloPortfolio:

    def __init__(self, file_path, capital=10000, max_weight=0.3):
        self.file_path = file_path
        self.capital = capital
        self.max_weight = max_weight
        
        self.returns_df = None
        self.mu = None
        self.cov_matrix = None
        self.stocks = None
        self.results = []

    def load_data(self):
        # Load returns (price-based)
        price_df = pd.read_excel(self.file_path, sheet_name="returns", index_col=0)
        returns = price_df.pct_change().dropna()

        self.cov_matrix = returns.cov().values
        self.stocks = returns.columns.tolist()

        # Load expected returns (your edge)
        exp_df = pd.read_excel(self.file_path, sheet_name="expected")
        self.mu = exp_df.set_index("Stock").loc[self.stocks]["ExpectedReturn"].values

    def generate_weights(self, n):
        weights = np.random.random(n)
        weights /= np.sum(weights)

        # Apply max cap
        weights = np.minimum(weights, self.max_weight)
        weights /= np.sum(weights)

        return weights

    def simulate(self, num_portfolios=20000):
        n = len(self.mu)

        for _ in range(num_portfolios):
            weights = self.generate_weights(n)

            port_return = np.dot(weights, self.mu)
            port_vol = np.sqrt(weights.T @ self.cov_matrix @ weights)
            sharpe = port_return / port_vol if port_vol != 0 else 0

            self.results.append({
                "return": port_return,
                "volatility": port_vol,
                "sharpe": sharpe,
                "weights": weights
            })

    def get_best(self):
        return max(self.results, key=lambda x: x["sharpe"])

    def build_output(self, best):
        df = pd.DataFrame({
            "Stock": self.stocks,
            "Weight": best["weights"]
        })

        df["Capital"] = df["Weight"] * self.capital

        # Map expected returns
        exp_df = pd.read_excel(self.file_path, sheet_name="expected")
        exp_map = dict(zip(exp_df["Stock"], exp_df["ExpectedReturn"]))

        df["Return"] = df["Stock"].map(exp_map)
        df["EP"] = df["Capital"] * df["Return"]

        return df

    def save_to_excel(self, df, filename="portfolio_output.xlsx"):
        df.to_excel(filename, index=False)

    def run(self, num_portfolios=20000, save=True):
        self.load_data()
        self.simulate(num_portfolios)
        best = self.get_best()

        print("\n===== BEST PORTFOLIO =====")
        print(f"Return: {best['return']:.2%}")
        print(f"Volatility: {best['volatility']:.2%}")
        print(f"Sharpe: {best['sharpe']:.2f}")

        output_df = self.build_output(best)

        if save:
            self.save_to_excel(output_df)

        return output_df
```

---

# ▶️ 3. HOW TO USE

```python
optimizer = MonteCarloPortfolio(
    file_path="portfolio_input.xlsx",
    capital=10000,
    max_weight=0.30
)

result = optimizer.run(num_portfolios=30000)

print(result)
```

---

# 🔥 4. WHAT MAKES THIS “EVERGREEN”

### ✔ Realistic

* Uses covariance (not fake independence)

### ✔ Flexible

* You control expected returns (seasonal, momentum, etc.)

### ✔ Scalable

* Works for 5 stocks → 500 stocks

### ✔ Safe

* Weight cap avoids concentration risk

---

# 🧠 5. INTERPRETING OUTPUT

Healthy output:

* Sharpe: **1 – 3**
* Volatility: realistic (10–25% annualized approx)
* Diversified weights

---

# ⚠️ 6. COMMON MISTAKES (avoid forever)

❌ Using only SD (no covariance)
❌ Sharpe > 5 (fake model)
❌ No weight cap
❌ Using raw returns without validation

---

# 🚀 7. NEXT LEVEL UPGRADES (future)

You can extend this into:

* Risk parity model
* Minimum variance portfolio
* Black–Litterman model
* Sector constraints
* Monthly rebalancing engine

---

# 🏁 FINAL SUMMARY

👉 You now have:

```text
Excel → Expected Returns → Covariance → Monte Carlo → Optimal Portfolio
```

👉 This is **real quant workflow**, not retail tricks

---

If you want next step, I can help you build:

* Auto **seasonal scanner → optimizer integration**
* Or **backtest engine (this is where money is proven)**

Just tell 👍
