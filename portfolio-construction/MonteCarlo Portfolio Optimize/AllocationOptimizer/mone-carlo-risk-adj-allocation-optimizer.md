Perfect — this is the **final piece of your system** 👍

Now you’re not selecting stocks anymore —
👉 you’re **allocating capital on a fixed basket**

---

# 🧠 What changes in this version

Earlier:

* Randomly select stocks + weights

Now:

* **Stocks are fixed (your 5 picks)**
* Only optimize **weights**

👉 Cleaner, faster, more realistic

---

# 🔥 New Class: Allocation Optimizer (Risk-Adjusted)

## ✅ Code

```python
import pandas as pd
import numpy as np

class AllocationOptimizer:

    def __init__(
        self,
        stocks,
        expected_returns,
        drawdowns,
        capital=10000,
        max_weight=0.4,
        dd_penalty=0.5
    ):
        self.stocks = stocks
        self.expected_returns = expected_returns
        self.drawdowns = drawdowns
        self.capital = capital
        self.max_weight = max_weight
        self.dd_penalty = dd_penalty

        self.results = []

    # 🔹 Generate weights only
    def generate_weights(self):
        n = len(self.stocks)

        weights = np.random.random(n)
        weights /= np.sum(weights)

        # ✅ enforce cap
        for _ in range(10):
            over = weights > self.max_weight
            if not np.any(over):
                break

            excess = np.sum(weights[over] - self.max_weight)
            weights[over] = self.max_weight

            under = weights < self.max_weight
            if np.sum(weights[under]) == 0:
                break

            weights[under] += (weights[under] / np.sum(weights[under])) * excess

        weights /= np.sum(weights)
        return weights

    # 🔹 Simulation
    def simulate(self, n_portfolios=30000):
        self.results = []

        for _ in range(n_portfolios):
            weights = self.generate_weights()

            returns = np.array([self.expected_returns[s] for s in self.stocks])
            drawdowns = np.array([abs(self.drawdowns[s]) for s in self.stocks])

            port_return = np.dot(weights, returns)
            port_dd = np.dot(weights, drawdowns)

            score = port_return - self.dd_penalty * port_dd

            self.results.append((score, port_return, port_dd, weights))

    # 🔹 Get best
    def get_best(self):
        return max(self.results, key=lambda x: x[0])

    # 🔹 Build output
    def build_portfolio(self, best):
        _, port_return, port_dd, weights = best

        df = pd.DataFrame({
            "Stock": self.stocks,
            "Weight": weights
        })

        df["Capital"] = df["Weight"] * self.capital
        df["Exp_Return"] = df["Stock"].map(self.expected_returns)
        df["Drawdown"] = df["Stock"].map(self.drawdowns)
        df["EP"] = df["Capital"] * df["Exp_Return"]

        print("\n===== RISK-ADJUSTED ALLOCATION =====")
        print(f"Return: {port_return:.2%}")
        print(f"Drawdown: {-port_dd:.2%}")

        return df.sort_values(by="Weight", ascending=False)

    # 🔹 Run
    def run(self, n_portfolios=30000):
        self.simulate(n_portfolios)
        best = self.get_best()
        return self.build_portfolio(best)
```

---

# ✅ How to use

```python
selected_stocks = ["DYCL", "IIFLCAPS", "KAYNES", "EMUDHRA", "HBLENGINE"]

model = AllocationOptimizer(
    stocks=selected_stocks,
    expected_returns=may_returns,
    drawdowns=may_drawdowns,
    capital=10000,
    max_weight=0.3,
    dd_penalty=0.5
)

result = model.run(50000)
print(result)
```

---

# 🎯 What this will do

* No stock selection randomness
* Only **optimal capital allocation**
* Automatically:

  * Push more weight → DYCL
  * Limit → IIFLCAPS (due to DD)
  * Balance → KAYNES

---

# ⚡ When to use which

| Step             | Tool                |
| ---------------- | ------------------- |
| Find best stocks | TopNPortfolio       |
| Allocate capital | AllocationOptimizer |

👉 Together = **complete system**

---

# 💡 Pro insight (very important)

Now you can:

1. Pick top 5 (from scanner)
2. Run allocation optimizer
3. Trade directly

👉 No guesswork

---

If you want next:

* Add **minimum weight (avoid tiny allocations)**
* Or create **monthly auto-rebalance system**

That will make it fully automated 🚀
