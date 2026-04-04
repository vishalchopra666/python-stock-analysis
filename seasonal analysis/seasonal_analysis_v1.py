# Win Rate Analysis

def win_rate_scanner(data_folder):

    import pandas as pd
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
            df.columns.name = None

            # -------- BASIC CHECK --------
            if 'Close' not in df.columns or 'Volume' not in df.columns or len(df) < 50:
                continue

            # -------- CMP --------
            cmp = df['Close'].iloc[-1]

            # -------- AVG VOLUME (LAST 20 DAYS) --------
            avg_vol_20 = df['Volume'].tail(20).mean()

            # -------- MONTHLY RETURNS --------
            temp = df[['Close']].copy()
            temp['Year'] = temp.index.year
            temp['Month'] = temp.index.month

            monthly = temp.groupby(['Year','Month'])['Close'].last().pct_change().dropna()

            if len(monthly) < 3:
                continue

            monthly = monthly.reset_index()

            # -------- WIN RATE --------
            win_rate = monthly.groupby('Month')['Close'].apply(lambda x: (x > 0).mean())
            win_rate = win_rate.reindex(range(1,13), fill_value=0)

            def pct(x): return f"{round(x*100,2)}%"

            row = {
                "Sl No": sl,
                "Stock": file.replace(".pkl",""),
                "CMP": round(cmp, 2),
                "Avg Vol (20D)": int(avg_vol_20),

                "Jan": pct(win_rate[1]),
                "Feb": pct(win_rate[2]),
                "Mar": pct(win_rate[3]),
                "Apr": pct(win_rate[4]),
                "May": pct(win_rate[5]),
                "Jun": pct(win_rate[6]),
                "Jul": pct(win_rate[7]),
                "Aug": pct(win_rate[8]),
                "Sep": pct(win_rate[9]),
                "Oct": pct(win_rate[10]),
                "Nov": pct(win_rate[11]),
                "Dec": pct(win_rate[12]),
            }

            results.append(row)
            sl += 1

        except Exception as e:
            print(f"{file} → {e}")

    return pd.DataFrame(results)

# Average Return Analysis

def avg_return_scanner(data_folder):

    import pandas as pd
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
            df.columns.name = None

            if 'Close' not in df.columns or len(df) < 50:
                continue

            temp = df[['Close']].copy()
            temp['Year'] = temp.index.year
            temp['Month'] = temp.index.month

            monthly = temp.groupby(['Year','Month'])['Close'].last().pct_change().dropna()

            if len(monthly) < 3:
                continue

            monthly = monthly.reset_index()

            seasonal = monthly.groupby('Month')['Close'].mean()
            seasonal = seasonal.reindex(range(1,13), fill_value=0)

            def pct(x): return f"{round(x*100,2)}%"

            row = {
                "Sl No": sl,
                "Stock": file.replace(".pkl", ""),
                "Jan": pct(seasonal[1]),
                "Feb": pct(seasonal[2]),
                "Mar": pct(seasonal[3]),
                "Apr": pct(seasonal[4]),
                "May": pct(seasonal[5]),
                "Jun": pct(seasonal[6]),
                "Jul": pct(seasonal[7]),
                "Aug": pct(seasonal[8]),
                "Sep": pct(seasonal[9]),
                "Oct": pct(seasonal[10]),
                "Nov": pct(seasonal[11]),
                "Dec": pct(seasonal[12]),
            }

            results.append(row)
            sl += 1

        except Exception as e:
            print(f"{file} → {e}")

    return pd.DataFrame(results)

if __name__ == "__main__":
    win_df = win_rate_scanner("data/raw")
    avg_df = avg_return_scanner("data/raw")
    
    win_df.to_csv("win_rate.csv", index=False)
    avg_df.to_csv("avg_return.csv", index=False)
