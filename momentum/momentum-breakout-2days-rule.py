# Ahh got it — you want a fresh momentum breakout, not a continuous trend.
# 
# Your logic (clean form):
# Today Close > all SMA
# Yesterday Close > all SMA
# Day -2 Close < all SMA → (breakout trigger)
# 
# So:
# 👉 first time crossing above all SMAs and sustaining for 2 days

def momentum_breakout_scanner(data_folder):

    import pandas as pd
    import os
    from tqdm import tqdm
    import openpyxl

    results = []
    sl = 1

    sma_periods = [5, 10, 15, 20, 30, 50, 100, 200]

    files = [
        f for f in os.listdir(data_folder)
        if f.endswith(".pkl") and f != "NIFTY_50.pkl"
    ]

    for file in tqdm(files):

        try:
            df = pd.read_pickle(os.path.join(data_folder, file))
            df = df.sort_index()
            df.columns.name = None

            if 'Close' not in df.columns or 'Volume' not in df.columns or len(df) < 205:
                continue

            temp = df[['Close', 'Volume']].copy()

            close_today = temp['Close'].iloc[-1]
            close_yesterday = temp['Close'].iloc[-2]
            close_2days = temp['Close'].iloc[-3]

            def pct(x): return f"{round(x*100,2)}%"

            sma_data = {}
            condition_pass = True

            for period in sma_periods:
                sma_series = temp['Close'].rolling(period).mean()

                sma_today = sma_series.iloc[-1]
                sma_yesterday = sma_series.iloc[-2]
                sma_2days = sma_series.iloc[-3]

                if pd.isna(sma_today) or pd.isna(sma_yesterday) or pd.isna(sma_2days):
                    condition_pass = False
                    break

                # --- Your logic ---
                if not (
                    close_today > sma_today and
                    close_yesterday > sma_yesterday and
                    close_2days < sma_2days
                ):
                    condition_pass = False
                    break

                ret = (close_today / sma_today) - 1
                sma_data[f"SMA {period}"] = pct(ret)

            if not condition_pass:
                continue

            # --- Volume Ratio ---
            avg_vol_20 = temp['Volume'].rolling(20).mean().iloc[-1]
            today_vol = temp['Volume'].iloc[-1]

            if pd.isna(avg_vol_20) or avg_vol_20 == 0:
                vol_ratio = "NA"
            else:
                vol_ratio = round(today_vol / avg_vol_20, 2)

            row = {
                "Sl No": sl,
                "Stock": file.replace(".pkl", ""),
                "CMP": round(close_today, 2),
                **sma_data,
                "Volume Ratio (20D)": vol_ratio,
                "avg_vol_20": avg_vol_20
            }

            results.append(row)
            sl += 1

        except Exception as e:
            print(f"{file} → {e}")

    return pd.DataFrame(results)


if __name__ == "__main__":
    df = momentum_breakout_scanner("../data/raw")
    df.to_excel("momentum_breakout_scan.xlsx", index=False, engine="openpyxl")
