Great — now we’ll build a **proper reusable system**:

👉 Excel → Python class → Monte Carlo → Optimal portfolio

Simple, clean, reusable.

---

# 📁 1. Excel Format (VERY IMPORTANT)

Create a file: `portfolio_input.xlsx`

### Sheet: `data`

| Stock      | Return | Volatility |
| ---------- | ------ | ---------- |
| BDL        | 0.16   | 0.0332     |
| AARTIPHARM | 0.13   | 0.0333     |
| ARE&M      | 0.07   | 0.0264     |

👉 Notes:

* Return = expected (your seasonal May)
* Volatility = 60 SD (in decimal, not %)

---

# 🧠 2. OOP Monte Carlo Engine

This is your reusable class:

```python
import pandas as pd
import numpy as np

class PortfolioOptimizer:
    
    def __init__(self, file_path, sheet_name="data", capital=10000):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.capital = capital
        self.df = None
        self.mu = None
        self.sigma = None
        self.results = []

    def load_data(self):
        self.df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
        self.mu = self.df["Return"].values
        self.sigma = self.df["Volatility"].values

    def simulate(self, num_portfolios=10000):
        n = len(self.mu)

        for _ in range(num_portfolios):
            weights = np.random.random(n)
            weights /= np.sum(weights)

            portfolio_return = np.dot(weights, self.mu)
            portfolio_vol = np.sqrt(np.sum((weights * self.sigma) ** 2))

            sharpe = portfolio_return / portfolio_vol

            self.results.append({
                "return": portfolio_return,
                "volatility": portfolio_vol,
                "sharpe": sharpe,
                "weights": weights
            })

    def get_best_portfolio(self):
        best = max(self.results, key=lambda x: x["sharpe"])
        return best

    def allocate(self, best):
        weights = best["weights"]
        self.df["Weight"] = weights
        self.df["Capital"] = self.df["Weight"] * self.capital
        self.df["EP"] = self.df["Capital"] * self.df["Return"]
        return self.df

    def run(self, num_portfolios=10000):
        self.load_data()
        self.simulate(num_portfolios)
        best = self.get_best_portfolio()
        final_df = self.allocate(best)

        print("Best Portfolio:")
        print(f"Return: {best['return']:.2%}")
        print(f"Volatility: {best['volatility']:.2%}")
        print(f"Sharpe: {best['sharpe']:.2f}")

        return final_df
```

---

# 🚀 3. How to Use

```python
optimizer = PortfolioOptimizer("portfolio_input.xlsx", capital=10000)
result = optimizer.run(num_portfolios=20000)

print(result)
```

---

# 🔥 4. What this does

* Tries **20,000 random portfolios**
* Picks **best Sharpe combination**
* Allocates capital automatically

---

# ⚠️ 5. IMPORTANT IMPROVEMENT (next step)

Right now:

```text
Assumes stocks are independent ❌
```

Better:

👉 Add correlation (covariance matrix)

We can upgrade this to:

```python
portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)
```

👉 This is REAL portfolio math (like funds use)

---

# 🧠 6. Why this is powerful

* No manual selection
* Finds hidden combinations
* Scales to 50–100 stocks
* Works perfectly with your seasonal returns

---

# 🔥 7. Optional upgrades (tell me next)

I can extend this into:

* ✅ Correlation-aware model (must-have)
* ✅ Weight constraints (max 10% per stock)
* ✅ Sector balancing
* ✅ Save output to Excel
* ✅ Backtest monthly rotation

---

# 🏁 Final thought

You just moved from:

```text
Stock picking → Portfolio engineering
```

👉 This is where real edge comes.

---

Say next:

👉 “add correlation”
or
👉 “add constraints + export excel”

We’ll make this **production-level system** 🚀
