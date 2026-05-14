def cup_handle_research(
    file_path,
    output_excel="cup_handle_report.xlsx",
    to_save="no",
    lookback=80,
    min_cup_depth=0.12,
    max_cup_depth=0.35,
    max_handle_depth=0.12,
    breakout_buffer=0.01,
    forward_days=[2, 3, 5, 10, 20,30,60]
):
    """
    =========================================================
    CUP & HANDLE RESEARCH ENGINE
    =========================================================

    PARAMETERS
    ----------
    file_path : str
        Path to stock OHLCV data

    output_excel : str
        Excel report output path

    RETURNS
    -------
    dict
        {
            "signals": [...],
            "summary": [...],
            "meta": {...}
        }

    =========================================================
    """

    import pandas as pd
    import numpy as np
    from pathlib import Path

    # =====================================================
    # LOAD FILE
    # =====================================================

    file_path = Path(file_path)

    ext = file_path.suffix.lower()

    if ext == ".csv":

        df = pd.read_csv(file_path)

    elif ext in [".pkl", ".pickle"]:

        df = pd.read_pickle(file_path)

    elif ext == ".parquet":

        df = pd.read_parquet(file_path)

    else:

        raise ValueError("Unsupported file format")

    # =====================================================
    # CLEAN COLUMNS
    # =====================================================

    df.columns = [c.lower() for c in df.columns]

    required_cols = [
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    missing = [
        c for c in required_cols
        if c not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing columns: {missing}"
        )

    # =====================================================
    # DATE INDEX
    # =====================================================

    if "date" in df.columns:

        df["date"] = pd.to_datetime(df["date"])

        df.set_index("date", inplace=True)

    elif not isinstance(df.index, pd.DatetimeIndex):

        df.index = pd.to_datetime(df.index)

    df = df.sort_index()

    # =====================================================
    # PREPARE
    # =====================================================

    close = df["close"]
    volume = df["volume"]

    volume_ma = volume.rolling(20).mean()

    signals = []

    # =====================================================
    # MAIN LOOP
    # =====================================================

    for i in range(
        lookback,
        len(df) - max(forward_days)
    ):

        try:

            # -------------------------------------------------
            # WINDOW
            # -------------------------------------------------

            window = df.iloc[i - lookback:i]

            # -------------------------------------------------
            # LEFT PEAK
            # -------------------------------------------------

            left_peak_price = window["close"].max()

            left_peak_idx = window["close"].idxmax()

            left_peak_pos = (
                window.index.get_loc(left_peak_idx)
            )

            # -------------------------------------------------
            # AFTER PEAK
            # -------------------------------------------------

            after_peak = window.iloc[left_peak_pos:]

            if len(after_peak) < 20:
                continue

            # -------------------------------------------------
            # CUP BOTTOM
            # -------------------------------------------------

            bottom_price = after_peak["close"].min()

            bottom_idx = after_peak["close"].idxmin()

            bottom_pos = (
                after_peak.index.get_loc(bottom_idx)
            )

            # -------------------------------------------------
            # CUP DEPTH
            # -------------------------------------------------

            cup_depth = (
                (left_peak_price - bottom_price)
                / left_peak_price
            )

            if not (
                min_cup_depth <= cup_depth <= max_cup_depth
            ):
                continue

            # -------------------------------------------------
            # RECOVERY
            # -------------------------------------------------

            after_bottom = after_peak.iloc[bottom_pos:]

            if len(after_bottom) < 10:
                continue

            right_peak = after_bottom["close"].max()

            if right_peak < left_peak_price * 0.95:
                continue

            # -------------------------------------------------
            # HANDLE
            # -------------------------------------------------

            handle = df.iloc[i - 10:i]

            handle_high = handle["close"].max()

            handle_low = handle["close"].min()

            handle_depth = (
                (handle_high - handle_low)
                / handle_high
            )

            if handle_depth > max_handle_depth:
                continue

            # -------------------------------------------------
            # BREAKOUT
            # -------------------------------------------------

            breakout_close = close.iloc[i]

            resistance = left_peak_price

            breakout_valid = (
                breakout_close >
                resistance * (1 + breakout_buffer)
            )

            if not breakout_valid:
                continue

            # -------------------------------------------------
            # VOLUME
            # -------------------------------------------------

            vol_ratio = (
                volume.iloc[i]
                / volume_ma.iloc[i]
            )

            if np.isnan(vol_ratio):
                continue

            # -------------------------------------------------
            # SIGNAL ROW
            # -------------------------------------------------

            row = {
                "date": str(df.index[i].date()),
                "breakout_close": round(
                    breakout_close,
                    2
                ),
                "resistance": round(
                    resistance,
                    2
                ),
                "cup_depth_pct": round(
                    cup_depth * 100,
                    2
                ),
                "handle_depth_pct": round(
                    handle_depth * 100,
                    2
                ),
                "volume_ratio": round(
                    vol_ratio,
                    2
                )
            }

            # -------------------------------------------------
            # FORWARD RETURNS
            # -------------------------------------------------

            for d in forward_days:

                future_close = close.iloc[i + d]

                ret = (
                    future_close / breakout_close
                ) - 1

                row[f"ret_{d}d_pct"] = round(
                    ret * 100,
                    2
                )

                row[f"win_{d}d"] = ret > 0

            signals.append(row)

        except:

            continue

    # =====================================================
    # SIGNALS DF
    # =====================================================

    signals_df = pd.DataFrame(signals)

    # =====================================================
    # SUMMARY
    # =====================================================

    summary_rows = []

    if len(signals_df) > 0:

        for d in forward_days:

            ret_col = f"ret_{d}d_pct"

            win_col = f"win_{d}d"

            summary_rows.append({

                "holding_days": d,

                "signals": int(
                    len(signals_df)
                ),

                "win_rate_pct": round(
                    signals_df[win_col]
                    .mean() * 100,
                    2
                ),

                "avg_return_pct": round(
                    signals_df[ret_col]
                    .mean(),
                    2
                ),

                "median_return_pct": round(
                    signals_df[ret_col]
                    .median(),
                    2
                ),

                "max_return_pct": round(
                    signals_df[ret_col]
                    .max(),
                    2
                ),

                "min_return_pct": round(
                    signals_df[ret_col]
                    .min(),
                    2
                )
            })

    summary_df = pd.DataFrame(summary_rows)

    # =====================================================
    # META
    # =====================================================

    meta = {

        "total_signals": int(
            len(signals_df)
        ),

        "average_volume_ratio": round(
            signals_df["volume_ratio"].mean(),
            2
        ) if len(signals_df) else None,

        "average_cup_depth_pct": round(
            signals_df["cup_depth_pct"].mean(),
            2
        ) if len(signals_df) else None,

        "average_handle_depth_pct": round(
            signals_df["handle_depth_pct"].mean(),
            2
        ) if len(signals_df) else None
    }

    # =====================================================
    # SAVE EXCEL
    # =====================================================
    if to_save == "yes":
        with pd.ExcelWriter(
            output_excel,
            engine="openpyxl"
        ) as writer:
    
            signals_df.to_excel(
                writer,
                sheet_name="Signals",
                index=False
            )
    
            summary_df.to_excel(
                writer,
                sheet_name="Summary",
                index=False
            )

        print("Report Saved to Excel file")

    # =====================================================
    # RETURN JSON
    # =====================================================

    result = {

        "signals": signals_df.to_dict(
            orient="records"
        ),

        "summary": summary_df.to_dict(
            orient="records"
        ),

        "meta": meta
    }

    return result

if __name__ == "__main__": 
    result = cup_handle_research(
        output_excel="cup_handle_ADANIPOWER.xlsx",
        file_path="data/raw/ADANIPOWER.pkl",
        to_save="yes"
    )
    summary_df = pd.DataFrame(
        result["summary"]
    )
    
    print(summary_df)
