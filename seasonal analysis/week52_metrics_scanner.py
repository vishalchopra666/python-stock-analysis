# Uses last ~252 trading days to approximate 52-week range
# Identifies 52-week high and low along with exact dates
# Measures how far current price is from key extremes (high/low)
# Calculates recency of highs/lows to understand trend strength
# Helps avoid falling knife by filtering stocks near recent lows
# Helps find momentum by identifying stocks near recent highs
# Can be combined with seasonal/expected return signals for better accuracy


def week52_metrics_scanner(data_folder):

    import pandas as pd
    import os
    from tqdm import tqdm

    results = []

    files = [
        f for f in os.listdir(data_folder)
        if f.endswith(".pkl") and f != "NIFTY_50.pkl"
    ]

    for file in tqdm(files):

        try:
            df = pd.read_pickle(os.path.join(data_folder, file))
            df = df.sort_index()

            if 'Close' not in df.columns or len(df) < 252:
                continue

            # --- Last 1 year (approx 252 trading days) ---
            df_52 = df.tail(252)

            # --- Current Price ---
            cmp = df_52['Close'].iloc[-1]

            # --- 52 Week High ---
            high = df_52['Close'].max()
            high_date = df_52['Close'].idxmax()

            # --- 52 Week Low ---
            low = df_52['Close'].min()
            low_date = df_52['Close'].idxmin()

            # --- Distance from CMP ---
            dist_from_high = ((cmp - high) / high) * 100
            dist_from_low = ((cmp - low) / low) * 100

            # --- Days from High/Low ---
            last_date = df_52.index[-1]
            days_from_high = (last_date - high_date).days
            days_from_low = (last_date - low_date).days

            results.append({
                "Stock": file.replace(".pkl", ""),
                "CMP": round(cmp, 2),
                "52W High": round(high, 2),
                "52W High Date": high_date.date(),
                "52W Low": round(low, 2),
                "52W Low Date": low_date.date(),
                "Dist from High %": round(dist_from_high, 2),
                "Dist from Low %": round(dist_from_low, 2),
                "Days Since High": days_from_high,
                "Days Since Low": days_from_low
            })

        except Exception as e:
            print(f"{file} → {e}")

    return pd.DataFrame(results)


if __name__ == "__main__":
    df = week52_metrics_scanner("data/raw")
    df.to_csv("week52_metrics.csv", index=False)
