"""Utility functions for time-related operations."""

import pandas as pd
from datetime import datetime, timedelta

# Time window constants
TIME_WINDOW_ALL = "All Time"
TIME_WINDOW_HOUR = "Last Hour"
TIME_WINDOW_DAY = "Last Day"
TIME_WINDOW_WEEK = "Last Week"
TIME_WINDOW_MONTH = "Last Month"

# List of all available time windows in display order
TIME_WINDOW_OPTIONS = [TIME_WINDOW_ALL, TIME_WINDOW_HOUR, TIME_WINDOW_DAY, TIME_WINDOW_WEEK, TIME_WINDOW_MONTH]


def filter_dataframe_by_time(df, time_window):
    if df is None or df.empty or time_window == TIME_WINDOW_ALL:
        return df

    now = datetime.utcnow()

    if time_window == TIME_WINDOW_HOUR:
        cutoff = now - timedelta(hours=1)
    elif time_window == TIME_WINDOW_DAY:
        cutoff = now - timedelta(days=1)
    elif time_window == TIME_WINDOW_WEEK:
        cutoff = now - timedelta(weeks=1)
    elif time_window == TIME_WINDOW_MONTH:
        cutoff = now - timedelta(days=30)
    else:
        # Unknown time window, return original dataframe
        return df

    if not pd.api.types.is_datetime64_any_dtype(df["created_timestamp"]):
        df["created_timestamp"] = pd.to_datetime(df["created_timestamp"])

    return df[df["created_timestamp"] >= cutoff]


def get_topic_description(universe, topic_name):
    """Get the description for a topic from the universe object."""
   
    if universe and "topics" in universe:
        for topic in universe.get("topics", []):
            if topic.get("name") == topic_name:
                return topic.get("description", "")
    return ""   
