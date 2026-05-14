import pandas as pd
import numpy as np
from pathlib import Path

# =====================================================
# SETTINGS
# =====================================================

DATA_FOLDER = Path("data/raw")
OUTPUT_FILE = "nr7_all_stocks_report.xlsx"

# =====================================================
# STORAGE
# =====================================================

all_signals = []
summary_list = []

# =====================================================
# PROCESS EACH STOCK
# =====================================================

for file in DATA_FOLDER.glob("*.pkl"):

    stock_name = file.stem

    try:

        # -----------------------------------------
        # LOAD DATA
        # -----------------------------------------

        df = pd.read_pickle(file)

        df = df.sort_index()
        df.columns.name = None
        df.columns = df.columns.astype(str)

        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']

        missing = [c for c in required_cols if c not in df.columns]

        if missing:
            print(f"Skipping {stock_name} - Missing columns")
            continue

        # -----------------------------------------
        # NR7 DETECTION
        # -----------------------------------------

        df['Range'] = df['High'] - df['Low']

        df['NR7'] = (
            df['Range']
            .rolling(7)
            .apply(lambda x: x.iloc[-1] == x.min(), raw=False)
        )

        df['NR7'] = df['NR7'].fillna(0).astype(bool)

        # -----------------------------------------
        # BREAKOUT
        # -----------------------------------------

        df['Prev_NR7_High'] = np.where(
            df['NR7'],
            df['High'],
            np.nan
        )

        df['Prev_NR7_High'] = df['Prev_NR7_High'].shift(1)

        df['Breakout'] = (
            df['Close'] > df['Prev_NR7_High']
        )

        df['Signal'] = df['Breakout']

        # -----------------------------------------
        # FUTURE RETURNS
        # -----------------------------------------

        df['Return_3D'] = (
            (df['Close'].shift(-3) / df['Close']) - 1
        ) * 100

        df['Return_5D'] = (
            (df['Close'].shift(-5) / df['Close']) - 1
        ) * 100

        df['Return_10D'] = (
            (df['Close'].shift(-10) / df['Close']) - 1
        ) * 100

        # -----------------------------------------
        # SIGNALS
        # -----------------------------------------

        signals = df[df['Signal']].copy()

        if len(signals) == 0:
            continue

        signals['Stock'] = stock_name

        signals = signals[[
            'Stock',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume',
            'Return_3D',
            'Return_5D',
            'Return_10D'
        ]]

        all_signals.append(signals)

        # -----------------------------------------
        # SUMMARY
        # -----------------------------------------

        summary = {

            'Stock': stock_name,

            'Signals': len(signals),

            '3D Win Rate': round(
                (signals['Return_3D'] > 0).mean() * 100,
                2
            ),

            '5D Win Rate': round(
                (signals['Return_5D'] > 0).mean() * 100,
                2
            ),

            '10D Win Rate': round(
                (signals['Return_10D'] > 0).mean() * 100,
                2
            ),

            'Avg 3D Return': round(
                signals['Return_3D'].mean(),
                2
            ),

            'Avg 5D Return': round(
                signals['Return_5D'].mean(),
                2
            ),

            'Avg 10D Return': round(
                signals['Return_10D'].mean(),
                2
            )
        }

        summary_list.append(summary)

        print(f"Done: {stock_name}")

    except Exception as e:

        print(f"Error in {stock_name}: {e}")

# =====================================================
# FINAL DATAFRAMES
# =====================================================

signals_df = pd.concat(all_signals)

summary_df = pd.DataFrame(summary_list)

# Rank by best 5D win rate
summary_df = summary_df.sort_values(
    by='5D Win Rate',
    ascending=False
)

# =====================================================
# SAVE TO EXCEL
# =====================================================

if len(all_signals) == 0:
    print("No signals found.")
else:

    signals_df = pd.concat(all_signals, ignore_index=True)

    summary_df = pd.DataFrame(summary_list)

    summary_df = summary_df.sort_values(
        by='5D Win Rate',
        ascending=False
    )

    try:

        with pd.ExcelWriter(
            OUTPUT_FILE,
            engine='openpyxl',
            mode='w'
        ) as writer:

            signals_df.to_excel(
                writer,
                sheet_name='All Signals',
                index=False
            )

            summary_df.to_excel(
                writer,
                sheet_name='Stock Summary',
                index=False
            )

        print(f"\nSaved: {OUTPUT_FILE}")

    except Exception as e:

        print("Excel save failed:")
        print(e)

print("\n===================================")
print("REPORT SAVED")
print(OUTPUT_FILE)
print("===================================")

print(summary_df.head(20))
