# Uses last ~252 trading days to approximate 52-week range
# Identifies 52-week high and low along with exact dates
# Measures how far current price is from key extremes (high/low)
# Calculates recency of highs/lows to understand trend strength
# Helps avoid falling knife by filtering stocks near recent lows
# Helps find momentum by identifying stocks near recent highs
# Tracks all-time high/low to understand long-term positioning
# Adds 55-day high/low for short-term breakout (turtle-style signals)
# Can be combined with seasonal/expected return signals for better accuracy


def high_low_metrics_scanner(data_folder):

    import pandas as pd
    import os
    from tqdm import tqdm
    import openpyxl

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

            # --- Current Price ---
            cmp = df['Close'].iloc[-1]

            # --- Last 1 year (52W) ---
            df_52 = df.tail(252)

            high_52 = df_52['Close'].max()
            high_52_date = df_52['Close'].idxmax()

            low_52 = df_52['Close'].min()
            low_52_date = df_52['Close'].idxmin()

            # --- Last 55 trading days ---
            df_55 = df.tail(55)

            high_55 = df_55['Close'].max()
            high_55_date = df_55['Close'].idxmax()

            low_55 = df_55['Close'].min()
            low_55_date = df_55['Close'].idxmin()

            # --- ALL TIME High / Low ---
            ath = df['Close'].max()
            ath_date = df['Close'].idxmax()

            atl = df['Close'].min()
            atl_date = df['Close'].idxmin()

            # --- Distance from CMP ---
            dist_from_high_52 = ((cmp - high_52) / high_52) * 100
            dist_from_low_52 = ((cmp - low_52) / low_52) * 100

            dist_from_high_55 = ((cmp - high_55) / high_55) * 100
            dist_from_low_55 = ((cmp - low_55) / low_55) * 100

            dist_from_ath = ((cmp - ath) / ath) * 100
            dist_from_atl = ((cmp - atl) / atl) * 100

            # --- Days from High/Low ---
            last_date = df.index[-1]

            days_from_high_52 = (last_date - high_52_date).days
            days_from_low_52 = (last_date - low_52_date).days

            days_from_high_55 = (last_date - high_55_date).days
            days_from_low_55 = (last_date - low_55_date).days

            days_from_ath = (last_date - ath_date).days
            days_from_atl = (last_date - atl_date).days

            results.append({
                "Stock": file.replace(".pkl", ""),
                "CMP": round(cmp, 2),

                "52W High": round(high_52, 2),
                "52W High Date": high_52_date.date(),
                "52W Low": round(low_52, 2),
                "52W Low Date": low_52_date.date(),

                "55D High": round(high_55, 2),
                "55D High Date": high_55_date.date(),
                "55D Low": round(low_55, 2),
                "55D Low Date": low_55_date.date(),

                "ATH": round(ath, 2),
                "ATH Date": ath_date.date(),
                "ATL": round(atl, 2),
                "ATL Date": atl_date.date(),

                "Dist from 52W High %": round(dist_from_high_52, 2),
                "Dist from 52W Low %": round(dist_from_low_52, 2),

                "Dist from 55D High %": round(dist_from_high_55, 2),
                "Dist from 55D Low %": round(dist_from_low_55, 2),

                "Dist from ATH %": round(dist_from_ath, 2),
                "Dist from ATL %": round(dist_from_atl, 2),

                "Days Since 52W High": days_from_high_52,
                "Days Since 52W Low": days_from_low_52,

                "Days Since 55D High": days_from_high_55,
                "Days Since 55D Low": days_from_low_55,

                "Days Since ATH": days_from_ath,
                "Days Since ATL": days_from_atl
            })

        except Exception as e:
            print(f"{file} → {e}")

    return pd.DataFrame(results)


if __name__ == "__main__":
    import pandas as pd
    df = high_low_metrics_scanner("data/raw")
    df.to_excel("week52_metrics.xlsx", index=False, engine="openpyxl")
