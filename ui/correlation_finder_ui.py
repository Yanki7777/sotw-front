"""Component for displaying correlation finder in Streamlit."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from api_client import APIClient


def display_correlation_finder():
    """
    Display the correlation finder interface in Streamlit.
    Allows users to select two feeds and displays a correlation plot with dual y-axes.
    """
    # Use container to isolate this component
    corr_container = st.container()

    with corr_container:
        st.title("📊 Correlation Finder")
        st.write("Select two data feeds to analyze for correlation over time.")

        # Get all universes
        universes = APIClient.get_all_universes()
        if not universes:
            st.warning("No universes available. Please check your data configuration.")
            return

        # Initialize feed selection state if needed
        for i in range(1, 3):
            if f"feed{i}_universe" not in st.session_state:
                st.session_state[f"feed{i}_universe"] = None
                st.session_state[f"feed{i}_topic"] = None
                st.session_state[f"feed{i}_source"] = None
                st.session_state[f"feed{i}_feature"] = None

        # Initialize plot data in session state if needed
        if "correlation_plot_data" not in st.session_state:
            st.session_state.correlation_plot_data = None
            st.session_state.correlation_value = None

        # Create two columns for feed selectors
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Feed 1")
            feed1 = select_feed(1, universes)

        with col2:
            st.subheader("Feed 2")
            feed2 = select_feed(2, universes)

        # Time window selection for the plot
        time_options = ["All Time", "Last Hour", "Last Day", "Last Week", "Last Month"]
        time_index = time_options.index("Last Day") if "Last Day" in time_options else 0
        if "correlation_time_window" not in st.session_state:
            st.session_state.correlation_time_window = time_options[time_index]

        time_window = st.selectbox(
            "Select Time Window:", time_options, index=time_index, key="correlation_time_selector"
        )
        st.session_state.correlation_time_window = time_window

        time_param = {"Last Hour": "hour", "Last Day": "day", "Last Week": "week", "Last Month": "month"}.get(
            time_window, "all"
        )

        # Generate correlation plot button
        if st.button("Generate Correlation Plot", type="primary", use_container_width=True, key="corr_gen_button"):
            if feed1 is not None and feed2 is not None:
                with st.spinner("Generating correlation plot..."):
                    fig = create_dual_axis_plot(feed1, feed2, time_param)
                    if fig:
                        st.session_state.correlation_plot_data = fig
                        # Calculate correlation coefficient
                        corr_value = calculate_correlation(feed1, feed2, time_param)
                        st.session_state.correlation_value = corr_value
                    else:
                        st.warning("Could not generate plot. Please check that both feeds have valid numeric data.")
            else:
                st.warning("Please select two complete feeds to generate a correlation plot.")

        # Display plot if it exists in session state
        if st.session_state.correlation_plot_data is not None:
            st.plotly_chart(st.session_state.correlation_plot_data, use_container_width=True)
            if st.session_state.correlation_value is not None:
                st.metric("Pearson Correlation Coefficient", f"{st.session_state.correlation_value:.4f}")


def select_feed(index, universes):
    """
    Creates a cascading selection interface for a single feed.
    Returns the selected feed as a dictionary or None if incomplete.
    """
    # Use session state keys for persistence
    prefix = f"feed{index}_"
    universe_key = f"{prefix}universe"
    topic_key = f"{prefix}topic"
    source_key = f"{prefix}source"
    feature_key = f"{prefix}feature"

    # Universe selection
    universe_options = {universe.get("universe_name"): universe for universe in universes}
    selected_universe_name = st.selectbox(
        "Select Universe:",
        options=list(universe_options.keys()),
        key=f"{prefix}universe_select",
        on_change=lambda: reset_selections(prefix, level="universe"),
    )

    # Store selected universe
    st.session_state[universe_key] = selected_universe_name

    # Get feed data for the selected universe
    feed_data = APIClient.get_feed_from_db(universe_name=selected_universe_name)
    if feed_data is None or feed_data.empty:
        st.warning(f"No data available for universe: {selected_universe_name}")
        return None

    # Topic selection - depends on universe
    topic_options = sorted(feed_data["topic"].unique().tolist())

    selected_topic = st.selectbox(
        "Select Topic:",
        options=topic_options,
        key=f"{prefix}topic_select",
        on_change=lambda: reset_selections(prefix, level="topic"),
    )

    # Store selected topic
    st.session_state[topic_key] = selected_topic

    # Source selection - depends on universe and topic
    topic_data = feed_data[feed_data["topic"] == selected_topic]
    source_options = sorted(topic_data["source"].unique().tolist())

    selected_source = st.selectbox(
        "Select Source:",
        options=source_options,
        key=f"{prefix}source_select",
        on_change=lambda: reset_selections(prefix, level="source"),
    )

    # Store selected source
    st.session_state[source_key] = selected_source

    # Feature selection - depends on universe, topic, and source
    topic_source_data = topic_data[topic_data["source"] == selected_source]
    feature_options = sorted(topic_source_data["feature_name"].unique().tolist())

    selected_feature = st.selectbox("Select Feature:", options=feature_options, key=f"{prefix}feature_select")

    # Store selected feature
    st.session_state[feature_key] = selected_feature

    # Return complete feed information
    return {
        "universe_name": selected_universe_name,
        "topic": selected_topic,
        "source": selected_source,
        "feature_name": selected_feature,
        "display_name": f"{selected_universe_name}: {selected_topic} - {selected_feature} ({selected_source})",
    }


def reset_selections(prefix, level):
    """Reset cascade selections below the specified level"""
    if level == "universe":
        st.session_state[f"{prefix}topic"] = None
        st.session_state[f"{prefix}source"] = None
        st.session_state[f"{prefix}feature"] = None
    elif level == "topic":
        st.session_state[f"{prefix}source"] = None
        st.session_state[f"{prefix}feature"] = None
    elif level == "source":
        st.session_state[f"{prefix}feature"] = None

    # Clear plot data when selections change
    st.session_state.correlation_plot_data = None
    st.session_state.correlation_value = None


def create_dual_axis_plot(feed1, feed2, time_window="all"):
    """
    Creates a plot with dual y-axes for comparing two different feeds over time.

    Parameters:
    - feed1: Dictionary with 'universe_name', 'topic', 'source', 'feature_name'
    - feed2: Dictionary with 'universe_name', 'topic', 'source', 'feature_name'
    - time_window: Time window to filter data ('all', 'hour', 'day', 'week', 'month')

    Returns:
    - Plotly figure object with dual y-axes
    """
    # Get data for both feeds
    df1 = get_feed_data(feed1, time_window)
    df2 = get_feed_data(feed2, time_window)

    if df1 is None or df2 is None or df1.empty or df2.empty:
        return None

    # Create figure with dual y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add trace for feed1
    fig.add_trace(
        go.Scatter(
            x=df1["created_timestamp"],
            y=df1["feature_value"],
            name=feed1["display_name"],
            line=dict(color="blue", width=2),
        ),
        secondary_y=False,
    )

    # Add trace for feed2
    fig.add_trace(
        go.Scatter(
            x=df2["created_timestamp"],
            y=df2["feature_value"],
            name=feed2["display_name"],
            line=dict(color="red", width=2),
        ),
        secondary_y=True,
    )

    # Set titles and labels
    fig.update_layout(
        title_text="Correlation Analysis with Dual Y-Axes",
        title_font_size=22,
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0.02)",
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(size=14)),
    )

    # Set x-axis title
    fig.update_xaxes(
        title_text="Date & Time", title_font=dict(size=16), gridcolor="rgba(0,0,0,0.1)", tickfont=dict(size=14)
    )

    # Set y-axes titles
    fig.update_yaxes(
        title_text=f"<b>{feed1['feature_name']}</b>",
        title_font=dict(color="blue", size=16),
        tickfont=dict(color="blue", size=14),
        gridcolor="rgba(0,0,0,0.1)",
        secondary_y=False,
    )

    fig.update_yaxes(
        title_text=f"<b>{feed2['feature_name']}</b>",
        title_font=dict(color="red", size=16),
        tickfont=dict(color="red", size=14),
        gridcolor="rgba(0,0,0,0.1)",
        secondary_y=True,
    )

    return fig


def get_feed_data(feed, time_window="all"):
    """
    Get data for a feed with filtering by time window.

    Parameters:
    - feed: Dictionary with 'universe_name', 'topic', 'source', 'feature_name'
    - time_window: Time window to filter data ('all', 'hour', 'day', 'week', 'month')

    Returns:
    - DataFrame with feed data or None
    """
    if feed is None:
        return None

    df = APIClient.get_feed_from_db(
        source=feed["source"],
        topic=feed["topic"],
        feature_name=feed["feature_name"],
        universe_name=feed["universe_name"],
    )

    if df is None or df.empty:
        return None

    # Filter by time window
    if time_window != "all":
        from datetime import datetime, timedelta

        now = datetime.now()
        if time_window == "hour":
            cutoff = now - timedelta(hours=1)
        elif time_window == "day":
            cutoff = now - timedelta(days=1)
        elif time_window == "week":
            cutoff = now - timedelta(weeks=1)
        elif time_window == "month":
            cutoff = now - timedelta(days=30)

        # Make sure created_timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(df["created_timestamp"]):
            df["created_timestamp"] = pd.to_datetime(df["created_timestamp"])

        df = df[df["created_timestamp"] >= cutoff]

    if df.empty:
        return None

    # Convert values to numeric
    try:
        df["feature_value"] = pd.to_numeric(df["feature_value"])
    except (ValueError, TypeError):
        return None

    # Sort by timestamp
    df = df.sort_values("created_timestamp")

    return df


def calculate_correlation(feed1, feed2, time_window="all"):
    """
    Calculate Pearson correlation coefficient between two feeds.

    Returns:
    - Correlation coefficient or None if calculation isn't possible
    """
    df1 = get_feed_data(feed1, time_window)
    df2 = get_feed_data(feed2, time_window)

    if df1 is None or df2 is None or df1.empty or df2.empty:
        return None

    # Create merged dataframe with aligned timestamps
    # Both datasets might have different timestamps, so we need to align them
    # We'll first convert them to series with timestamps as index
    s1 = pd.Series(df1["feature_value"].values, index=df1["created_timestamp"])
    s2 = pd.Series(df2["feature_value"].values, index=df2["created_timestamp"])

    # Combine and resample to common frequency
    combined = pd.concat([s1, s2], axis=1)
    combined.columns = ["feed1", "feed2"]

    # Drop rows with NaN values (timestamps that don't appear in both datasets)
    combined = combined.dropna()

    if len(combined) < 2:
        return None

    # Calculate Pearson correlation
    correlation = combined["feed1"].corr(combined["feed2"])

    return correlation
