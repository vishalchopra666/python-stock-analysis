# Count unique years present in data
# Detect actual data availability (years count)
# Avoid fake signals from low history
# Count how many unique years of historical data exist per stock to filter out unreliable / insufficient data
# Solve data quality issue, especially for yFinance API

def data_years_scanner(data_folder):

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

            if len(df) == 0:
                continue

            df = df.sort_index()

            # Extract years
            years = df.index.year.unique()
            year_count = len(years)

            results.append({
                "Stock": file.replace(".pkl", ""),
                "Years": year_count
            })

        except Exception as e:
            print(f"{file} → {e}")

    return pd.DataFrame(results)


if __name__ == "__main__":
    df = data_years_scanner("data/raw")
    df.to_csv("data_years.csv", index=False)
