def std_scanner(data_folder):

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

            if 'Close' not in df.columns or len(df) < 100:
                continue

            temp = df[['Close']].copy()
            temp['ret'] = temp['Close'].pct_change()

            # rolling std
            temp['std_20'] = temp['ret'].rolling(20).std()
            temp['std_60'] = temp['ret'].rolling(60).std()

            temp['Month'] = temp.index.month

            # monthly average of rolling std
            std20 = temp.groupby('Month')['std_20'].mean()
            std60 = temp.groupby('Month')['std_60'].mean()

            std20 = std20.reindex(range(1,13), fill_value=0)
            std60 = std60.reindex(range(1,13), fill_value=0)

            def pct(x): return f"{round(x*100,2)}%"

            row = {
                "Sl No": sl,
                "Stock": file.replace(".pkl", ""),

                # 20-day std
                "Jan_20": pct(std20[1]),
                "Feb_20": pct(std20[2]),
                "Mar_20": pct(std20[3]),
                "Apr_20": pct(std20[4]),
                "May_20": pct(std20[5]),
                "Jun_20": pct(std20[6]),
                "Jul_20": pct(std20[7]),
                "Aug_20": pct(std20[8]),
                "Sep_20": pct(std20[9]),
                "Oct_20": pct(std20[10]),
                "Nov_20": pct(std20[11]),
                "Dec_20": pct(std20[12]),

                # 60-day std
                "Jan_60": pct(std60[1]),
                "Feb_60": pct(std60[2]),
                "Mar_60": pct(std60[3]),
                "Apr_60": pct(std60[4]),
                "May_60": pct(std60[5]),
                "Jun_60": pct(std60[6]),
                "Jul_60": pct(std60[7]),
                "Aug_60": pct(std60[8]),
                "Sep_60": pct(std60[9]),
                "Oct_60": pct(std60[10]),
                "Nov_60": pct(std60[11]),
                "Dec_60": pct(std60[12]),
            }

            results.append(row)
            sl += 1

        except Exception as e:
            print(f"{file} → {e}")

    return pd.DataFrame(results)
