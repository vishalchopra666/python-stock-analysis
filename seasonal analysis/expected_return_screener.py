def expected_return_screener(data_folder):

    import pandas as pd
    import numpy as np
    import os
    from tqdm import tqdm

    results = []
    sl = 1

    files = [
        f for f in os.listdir(data_folder)
        if f.endswith(".pkl") and f != "NIFTY_50.pkl"
    ]

    for file in tqdm(files):

        try:
            df = pd.read_pickle(os.path.join(data_folder, file))
            df = df.sort_index()

            if 'Close' not in df.columns or len(df) < 100:
                continue

            temp = df[['Close']].copy()
            temp['Year'] = temp.index.year
            temp['Month'] = temp.index.month

            monthly = temp.groupby(['Year','Month'])['Close'].last().pct_change().dropna()
            monthly = monthly.reset_index()

            if len(monthly) < 10:
                continue

            for m in range(1, 13):

                data = monthly[monthly['Month'] == m]['Close']

                if len(data) < 5:
                    continue

                # --- BASIC METRICS ---
                mean_ret = data.mean()
                median_ret = data.median()
                std_dev = data.std()
                win_rate = (data > 0).mean()
                sample = len(data)

                # --- MODE (rounded) ---
                rounded = data.round(2)
                mode_ret = rounded.mode().iloc[0] if not rounded.mode().empty else np.nan

                # --- WEIGHTED MEAN (recent bias) ---
                years = monthly[monthly['Month'] == m]['Year']
                weights = years - years.min() + 1
                weighted_ret = np.average(data, weights=weights)

                # --- CAPM (placeholder) ---
                capm_ret = np.nan  # plug later

                def pct(x): 
                    return round(x * 100, 2)

                results.append({
                    "Sl No": sl,
                    "Stock": file.replace(".pkl", ""),
                    "Month": m,
                    "Mean %": pct(mean_ret),
                    "Median %": pct(median_ret),
                    "Mode %": pct(mode_ret) if not np.isnan(mode_ret) else None,
                    "Weighted %": pct(weighted_ret),
                    "Win Rate %": round(win_rate * 100, 2),
                    "Volatility %": pct(std_dev),
                    "Samples": sample,
                    "CAPM %": capm_ret
                })

            sl += 1

        except Exception as e:
            print(f"{file} → {e}")

    return pd.DataFrame(results)


if __name__ == "__main__":
    df = expected_return_screener("data/raw")
    df.to_csv("expected_return_screener.csv", index=False)
