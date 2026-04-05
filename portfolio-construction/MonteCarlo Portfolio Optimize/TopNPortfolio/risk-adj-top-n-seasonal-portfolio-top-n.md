# Top-N Seasonal Portfolio (Risk-Adjusted Monte Carlo)

## Introduction

Most trading systems focus only on **returns**.
But in real markets, what matters equally is **how much you lose along the way**.

A strategy that gives 40% return but falls 20% in between is very different from one that gives 30% return with only 3–4% drawdown.

This model solves that problem.

It combines:

* Seasonal stock selection
* Monte Carlo simulation
* Drawdown-based risk control
* Position sizing with max weight constraint

👉 Result: a **practical, tradable portfolio**

---

## Why Traditional Monte Carlo Fails

Standard Monte Carlo optimization:

* Maximizes return
* Allocates heavily to top-performing stocks
* Ignores downside risk

Typical outcome:

* 80–90% capital in 1–2 stocks ❌
* Very fragile portfolio

---

## Core Idea of This Model

Instead of optimizing only for return:

> We optimize for **Return – Risk (Drawdown)**

---

## Strategy Logic

For each simulation:

1. Randomly select N stocks
2. Assign random weights
3. Apply max weight constraint
4. Calculate:

   * Portfolio return
   * Portfolio drawdown
5. Compute score:

[
Score = Return - \lambda \times Drawdown
]

Where:

* Return = weighted expected return
* Drawdown = weighted downside risk
* λ (dd_penalty) = risk sensitivity

---

## Key Features

### 1. Drawdown Measurement

* Uses real downside risk instead of volatility
* Penalizes unstable stocks

### 2. Max Weight Constraint

* Prevents over-concentration
* Ensures diversification

### 3. Monte Carlo Simulation

* Explores thousands of combinations
* Finds best possible allocation

---

## Python Implementation

Below is the complete working code:

# Top-N Seasonal Portfolio (Risk-Adjusted Monte Carlo)
# Drawdown Measurement
# Max Weight + Min Weight


import pandas as pd
import numpy as np
import random

class TopNPortfolio:

    def __init__(
        self,
        stocks,
        expected_returns,
        drawdowns,
        capital=10000,
        n_select=5,
        max_weight=0.4,
        min_weight=0.05,   # 🔥 NEW
        dd_penalty=0.5
    ):
        self.stocks = stocks
        self.expected_returns = expected_returns
        self.drawdowns = drawdowns
        self.capital = capital
        self.n_select = n_select
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.dd_penalty = dd_penalty

        self.results = []

    # 🔹 Prepare maps + validation
    def prepare_data(self):
        self.mu_map = self.expected_returns
        self.dd_map = self.drawdowns

        # ✅ sanity check
        for s in self.stocks:
            if self.mu_map[s] < 0:
                raise ValueError(f"Return is negative for {s} ❌")
            if self.dd_map[s] > 0:
                raise ValueError(f"Drawdown should be negative for {s} ❌")

        # ✅ min weight feasibility check
        if self.min_weight * self.n_select > 1:
            raise ValueError("min_weight too high for given n_select ❌")

    # 🔹 Generate subset + weights
    def generate_portfolio(self):
        selected = random.sample(self.stocks, self.n_select)

        weights = np.random.random(self.n_select)
        weights /= np.sum(weights)

        # 🔹 enforce min weight
        weights = np.maximum(weights, self.min_weight)
        weights /= np.sum(weights)

        # 🔹 enforce max weight
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

        # 🔹 final normalize
        weights /= np.sum(weights)

        return selected, weights

    # 🔹 Simulation (RETURN + DRAWDOWN)
    def simulate(self, n_portfolios=30000):
        self.results = []

        for _ in range(n_portfolios):
            selected, weights = self.generate_portfolio()

            returns = np.array([self.mu_map[s] for s in selected])
            drawdowns = np.array([abs(self.dd_map[s]) for s in selected])

            port_return = np.dot(weights, returns)
            port_dd = np.dot(weights, drawdowns)

            # 🔥 risk-adjusted score
            score = port_return - self.dd_penalty * port_dd

            self.results.append((score, port_return, port_dd, selected, weights))

    # 🔹 Get best portfolio
    def get_best(self):
        return max(self.results, key=lambda x: x[0])

    # 🔹 Build output
    def build_portfolio(self, best):
        _, port_return, port_dd, selected, weights = best

        df = pd.DataFrame({
            "Stock": selected,
            "Weight": weights
        })

        df["Capital"] = df["Weight"] * self.capital
        df["Exp_Return"] = df["Stock"].map(self.expected_returns)
        df["Drawdown"] = df["Stock"].map(self.drawdowns)
        df["EP"] = df["Capital"] * df["Exp_Return"]

        print("\n===== RISK-ADJUSTED (TOP-N) =====")
        print(f"Return: {port_return:.2%}")
        print(f"Drawdown: {-port_dd:.2%}")

        print("\nDEBUG CHECK:")
        for s in selected:
            print(s, "| Return:", self.expected_returns[s],
                     "| DD:", self.drawdowns[s])

        return df.sort_values(by="Weight", ascending=False)

    # 🔹 Run
    def run(self, n_portfolios=30000):
        self.prepare_data()
        self.simulate(n_portfolios)
        best = self.get_best()
        return self.build_portfolio(best)


if __name__ == "__main__":
    edf = pd.read_excel("monte.xlsx")
    
    stocks = edf['Stock'].tolist()
    expected_returns = dict(zip(edf['Stock'], edf['Return']))
    drawdown = dict(zip(edf['Stock'], edf['drawdown']))

    model = TopNPortfolio(
        stocks,
        expected_returns,
        drawdown,
        capital=12000,
        max_weight=0.30,
        min_weight=0.05,   # 🔥 NEW PARAM
        n_select=5
    )

    result = model.run(40000)
    print(result)

---

## How to Use

1. Prepare your Excel file (`monte.xlsx`) with:

   * Stock
   * Return
   * Drawdown

2. Run the script

3. Get:

   * Optimal stock selection
   * Capital allocation
   * Expected portfolio return
   * Expected drawdown

---

## Parameter Guide

### n_select

* 5 → concentrated portfolio
* 10 → diversified

### max_weight

* 0.3 → balanced
* 0.5 → aggressive

### dd_penalty

* 0.2 → high return focus
* 0.5 → balanced
* 1.0 → conservative

---

## Example Insight

The model typically produces:

* 2–3 core stocks (high weight)
* 2–3 satellite stocks (low weight)

👉 This mirrors real portfolio construction

---

## Advantages

* Avoids over-concentration
* Controls downside risk
* Works perfectly with seasonal strategies
* Simple, fast, and scalable

---

## Final Thought

Most traders focus on **how much they can earn**.

Professionals focus on:

> How much they can lose — and still survive.

This system bridges that gap.

---

## Future Improvements

* Add win-rate into scoring
* Multi-month seasonal blending
* Portfolio rebalancing
* Automated pipeline

---

## Conclusion

This is not just a stock picker.

It is a **complete portfolio construction framework**
built for real-world trading.
