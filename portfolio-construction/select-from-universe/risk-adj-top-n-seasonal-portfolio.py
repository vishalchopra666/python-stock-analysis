* Top-N Seasonal Portfolio (Risk-Adjusted Monte Carlo)


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
        dd_penalty=0.5
    ):
        self.stocks = stocks
        self.expected_returns = expected_returns
        self.drawdowns = drawdowns
        self.capital = capital
        self.n_select = n_select
        self.max_weight = max_weight
        self.dd_penalty = dd_penalty

        self.results = []

    # 🔹 Prepare maps + validation
    def prepare_data(self):
        self.mu_map = self.expected_returns
        self.dd_map = self.drawdowns

        # ✅ sanity check (VERY IMPORTANT)
        for s in self.stocks:
            if self.mu_map[s] < 0:
                raise ValueError(f"Return is negative for {s} ❌")
            if self.dd_map[s] > 0:
                raise ValueError(f"Drawdown should be negative for {s} ❌")

    # 🔹 Generate subset + weights (FIXED + STABLE)
    def generate_portfolio(self):
        selected = random.sample(self.stocks, self.n_select)

        weights = np.random.random(self.n_select)
        weights /= np.sum(weights)

        # ✅ enforce cap properly
        for _ in range(10):  # limited iterations (stable)
            over = weights > self.max_weight
            if not np.any(over):
                break

            excess = np.sum(weights[over] - self.max_weight)
            weights[over] = self.max_weight

            under = weights < self.max_weight
            if np.sum(weights[under]) == 0:
                break

            weights[under] += (weights[under] / np.sum(weights[under])) * excess

        weights /= np.sum(weights)  # final normalize

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

    # 🔹 Build output (FIXED NAMES)
    def build_portfolio(self, best):
        _, port_return, port_dd, selected, weights = best

        df = pd.DataFrame({
            "Stock": selected,
            "Weight": weights
        })

        df["Capital"] = df["Weight"] * self.capital

        # ✅ clear naming (no confusion)
        df["Exp_Return"] = df["Stock"].map(self.expected_returns)
        df["Drawdown"] = df["Stock"].map(self.drawdowns)

        df["EP"] = df["Capital"] * df["Exp_Return"]

        print("\n===== RISK-ADJUSTED (TOP-N) =====")
        print(f"Return: {port_return:.2%}")
        print(f"Drawdown: {-port_dd:.2%}")

        # ✅ debug print (optional but useful)
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
    import pandas as pd
    edf = pd.read_excel("monte.xlsx")
    
    stocks = edf['Stock'].tolist()
    expected_returns = dict(zip(edf['Stock'], edf['Return']))
    drawdown = dict(zip(edf['Stock'], edf['drawdown']))

    model = TopNPortfolio(
      stocks,
      expected_returns,
      drawdown,
      max_weight=0.3,
      n_select=5   # 🔥 choose 5 or 10
    )

    result = model.run(50000)
    print(result)

        
