def monthly_drawdown_scanner(data_folder):

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

            monthly_dd = []

            for (y, m), group in temp.groupby(['Year', 'Month']):

                start_price = group['Close'].iloc[0]
                min_price = group['Close'].min()

                dd = (min_price - start_price) / start_price
                monthly_dd.append([m, dd])

            monthly_dd = pd.DataFrame(monthly_dd, columns=['Month', 'DD'])

            seasonal_dd = monthly_dd.groupby('Month')['DD'].mean()
            seasonal_dd = seasonal_dd.reindex(range(1,13), fill_value=0)

            def pct(x): return f"{round(x*100,2)}%"

            row = {
                "Sl No": sl,
                "Stock": file.replace(".pkl", ""),
                "Jan": pct(seasonal_dd[1]),
                "Feb": pct(seasonal_dd[2]),
                "Mar": pct(seasonal_dd[3]),
                "Apr": pct(seasonal_dd[4]),
                "May": pct(seasonal_dd[5]),
                "Jun": pct(seasonal_dd[6]),
                "Jul": pct(seasonal_dd[7]),
                "Aug": pct(seasonal_dd[8]),
                "Sep": pct(seasonal_dd[9]),
                "Oct": pct(seasonal_dd[10]),
                "Nov": pct(seasonal_dd[11]),
                "Dec": pct(seasonal_dd[12]),
            }

            results.append(row)
            sl += 1

        except Exception as e:
            print(f"{file} → {e}")

    return pd.DataFrame(results)
