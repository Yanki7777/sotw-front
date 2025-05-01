"""Utility functions for time-related operations."""

import pandas as pd
from datetime import datetime, timedelta


def filter_dataframe_by_time(df, time_window):
    """
    Filter dataframe based on time window.

    Parameters:
    - df: DataFrame with a timestamp column (created_timestamp or original_timestamp)
    - time_window: String time window ('all', 'hour', 'day', 'week', 'month') or timedelta parameter

    Returns:
    - Filtered dataframe
    """
    if df is None or df.empty:
        return df

    if time_window == "all":
        return df

    now = datetime.now()

    # Get the timestamp column to use (prefer created_timestamp if available)
    timestamp_col = "created_timestamp" if "created_timestamp" in df.columns else "original_timestamp"

    # Convert time_window to a timedelta cutoff
    if isinstance(time_window, str):
        if time_window == "hour":
            cutoff = now - timedelta(hours=1)
        elif time_window == "day":
            cutoff = now - timedelta(days=1)
        elif time_window == "week":
            cutoff = now - timedelta(weeks=1)
        elif time_window == "month":
            cutoff = now - timedelta(days=30)
        else:
            return df  # Unknown time window
    else:
        # Assume time_window is already a timedelta
        cutoff = now - time_window

    # Make sure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])

    return df[df[timestamp_col] >= cutoff]


def parse_time_window(time_window_str):
    """
    Convert a time window string to the corresponding parameter.

    Parameters:
    - time_window_str: String like 'All Time', 'Last Hour', etc.

    Returns:
    - Time parameter string ('all', 'hour', 'day', 'week', 'month')
    """
    return {"Last Hour": "hour", "Last Day": "day", "Last Week": "week", "Last Month": "month"}.get(
        time_window_str, "all"
    )
