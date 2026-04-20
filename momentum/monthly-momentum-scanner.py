# This is a pure momentum timeline scanner, not averaging, just real price movement month-by-month.
# 
# Key logic (important)
# Each month = (last price of month / first price of month) - 1
# Current month = (today price / first day of current month) - 1
# Last 12 months → rolling backward from current month
# If data missing → fill "NA"

def monthly_momentum_scanner(data_folder):

    import pandas as pd
    import os
    from tqdm import tqdm
    import openpyxl

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
            df.columns.name = None

            if 'Close' not in df.columns or 'Volume' not in df.columns or len(df) < 60:
                continue

            temp = df[['Close', 'Volume']].copy()

            # --- CMP ---
            latest_close = temp['Close'].iloc[-1]

            # --- Volume ---
            avg_vol_20 = temp['Volume'].rolling(20).mean().iloc[-1]
            today_vol = temp['Volume'].iloc[-1]

            if pd.isna(avg_vol_20) or avg_vol_20 == 0:
                vol_ratio = "NA"
                avg_vol_20 = "NA"
            else:
                vol_ratio = round(today_vol / avg_vol_20, 2)
                avg_vol_20 = int(avg_vol_20)

            # --- Monthly Returns ---
            temp['Year'] = temp.index.year
            temp['Month'] = temp.index.month

            grouped = temp.groupby(['Year', 'Month'])['Close']

            month_data = []
            for (y, m), group in grouped:
                first = group.iloc[0]
                last = group.iloc[-1]
                ret = (last / first) - 1
                month_data.append(((y, m), ret))

            # Convert to dict for easy lookup
            month_dict = {k: v for k, v in month_data}

            # Last 12 months (including current)
           # Last 12 months (including current)
            last_date = temp.index[-1]
            months = []
            
            for i in range(12):
                dt = (last_date - pd.DateOffset(months=i))
                key = (dt.year, dt.month)
                label = dt.strftime("%b-%Y")   # ✅ real month name
            
                months.append((key, label))
            
            def pct(x): return f"{round(x*100,2)}%" if x != "NA" else "NA"
            
            month_cols = {}
            
            for key, label in months:
            
                if key in month_dict:
                    month_cols[label] = pct(month_dict[key])
                else:
                    month_cols[label] = "NA"

            row = {
                "Sl No": sl,
                "Stock": file.replace(".pkl", ""),
                "CMP": round(latest_close, 2),
                "Avg Vol (20D)": avg_vol_20,
                "Volume Ratio": vol_ratio,
                **month_cols
            }

            results.append(row)
            sl += 1

        except Exception as e:
            print(f"{file} → {e}")

    return pd.DataFrame(results)


if __name__ == "__main__":
    df = monthly_momentum_scanner("../data/new_raw_20_04_2026")
    df.to_excel("monthly_momentum.xlsx", index=False, engine="openpyxl")
