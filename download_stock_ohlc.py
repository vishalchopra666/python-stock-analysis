import yfinance as yf
import pandas as pd
import os
import time

def download_stock_data(
    symbols,
    start_date="2005-01-01",
    batch_size=50,
    delay=5,
    max_retries=3,
    save_path="data",
    index__ = "NS"
):
    """
    Download historical stock data from yfinance in batches.

    Parameters:
    - symbols: list of stock symbols (without .NS)
    - start_date: start date for data
    - batch_size: number of stocks per batch
    - delay: delay (seconds) between batches
    - max_retries: retry attempts per batch
    - save_path: folder to save parquet files
    """

    # Ensure folder exists
    os.makedirs(save_path, exist_ok=True)

    # Convert to NSE format
    tickers = [s + index__ for s in symbols]

    total = len(tickers)
    print(f"Total Stocks: {total}")

    for i in range(0, total, batch_size):
        batch = tickers[i:i + batch_size]
        print(f"\n📦 Batch {i} → {i + len(batch)}")

        success = False

        for attempt in range(max_retries):
            try:
                data = yf.download(
                    batch,
                    start=start_date,
                    interval="1d",
                    group_by="ticker",
                    threads=True,
                    progress=False
                )

                success = True
                break

            except Exception as e:
                print(f"Retry {attempt + 1} failed: {e}")
                time.sleep(3)

        if not success:
            print("❌ Skipping batch due to repeated failure")
            continue

        # Save individual files
        for ticker in batch:
            try:
                df = data[ticker].dropna()

                if df.empty:
                    print(f"⚠️ No data: {ticker}")
                    continue

                file_name = ticker.replace(".NS", "")
                file_base = f"{save_path}/{file_name}"

                try:
                    df.to_parquet(file_base + ".parquet", engine="pyarrow")
                except Exception:
                    df.to_pickle(file_base + ".pkl")

            except Exception as e:
                print(f"Error saving {ticker}: {e}")

        print(f"⏳ Sleeping {delay} sec...")
        time.sleep(delay)

    print("\n✅ Download Completed")

if __name__ == "__main__":
    # stocks_list = ["RELIANCE", "360ONE"];
    # download_stock_data(stocks_list)
