def momentum_scanner(data_folder):

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

            if 'Close' not in df.columns or 'Volume' not in df.columns or len(df) < 200:
                continue

            temp = df[['Close', 'Volume']].copy()

            # --- CMP ---
            latest_close = temp['Close'].iloc[-1]

            def pct(x): return f"{round(x*100,2)}%"

            sma_data = {}

            # --- SMA Returns ---
            for period in sma_periods:
                sma = temp['Close'].rolling(period).mean().iloc[-1]

                if pd.isna(sma):
                    sma_data[f"SMA {period}"] = "NA"
                else:
                    ret = (latest_close / sma) - 1
                    sma_data[f"SMA {period}"] = pct(ret)

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
                "CMP": round(latest_close, 2),   # ✅ added here
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
    df = momentum_scanner("../data/raw")
    df.to_excel("momentum_scan.xlsx", index=False, engine="openpyxl")
