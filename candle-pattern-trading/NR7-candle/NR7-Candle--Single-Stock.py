# NR7 + Breakout Scanner
# -----------------------------------------
# Detects:
# 1. NR7 candle
# 2. Next day breakout above NR7 high
# 3. Calculates future returns
# 4. Saves report to Excel
#
# Input:
# One stock .pkl file
#
# Output:
# Excel report with all signals


import pandas as pd
import numpy as np

# -----------------------------------------
# SETTINGS
# -----------------------------------------

FILE_PATH = "data/raw/RELIANCE.pkl"
OUTPUT_FILE = "nr7_breakout_report.xlsx"

# -----------------------------------------
# LOAD DATA
# -----------------------------------------

df = pd.read_pickle(FILE_PATH)

df = df.sort_index()
df.columns.name = None
df.columns = df.columns.astype(str)

required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']

for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"{col} column missing")

# -----------------------------------------
# NR7 DETECTION
# -----------------------------------------

# Daily range
df['Range'] = df['High'] - df['Low']

# Lowest range of last 7 candles
df['NR7'] = (
    df['Range']
    .rolling(7)
    .apply(lambda x: x.iloc[-1] == x.min(), raw=False)
)

df['NR7'] = df['NR7'].fillna(0).astype(bool)

# -----------------------------------------
# BREAKOUT CONDITION
# -----------------------------------------

# Next day closes above NR7 high
df['Prev_NR7_High'] = np.where(
    df['NR7'],
    df['High'],
    np.nan
)

df['Prev_NR7_High'] = df['Prev_NR7_High'].shift(1)

df['Breakout'] = (
    df['Close'] > df['Prev_NR7_High']
)

# Final signal
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
# EXTRACT SIGNALS
# -----------------------------------------

signals = df[df['Signal']].copy()

signals = signals[[
    'Open',
    'High',
    'Low',
    'Close',
    'Volume',
    'Return_3D',
    'Return_5D',
    'Return_10D'
]]

# -----------------------------------------
# WIN RATE ANALYSIS
# -----------------------------------------

summary = pd.DataFrame({

    'Metric': [

        'Total Signals',

        '3D Win Rate',
        '5D Win Rate',
        '10D Win Rate',

        'Average 3D Return',
        'Average 5D Return',
        'Average 10D Return'
    ],

    'Value': [

        len(signals),

        round((signals['Return_3D'] > 0).mean() * 100, 2),
        round((signals['Return_5D'] > 0).mean() * 100, 2),
        round((signals['Return_10D'] > 0).mean() * 100, 2),

        round(signals['Return_3D'].mean(), 2),
        round(signals['Return_5D'].mean(), 2),
        round(signals['Return_10D'].mean(), 2),
    ]
})

# -----------------------------------------
# SAVE TO EXCEL
# -----------------------------------------

with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:

    signals.to_excel(
        writer,
        sheet_name='Signals',
        index=True
    )

    summary.to_excel(
        writer,
        sheet_name='Summary',
        index=False
    )

print(f"\nSaved report: {OUTPUT_FILE}")
print(summary)
