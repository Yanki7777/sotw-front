"""Streamlit component for displaying correlation finder."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.api_client import APIClient
from utils.time_utils import filter_dataframe_by_time, TIME_WINDOW_OPTIONS, TIME_WINDOW_DAY


def display_correlation_finder():
    st.title("📊 Correlation Finder")
    st.write("Select two data feeds to analyze their correlation.")

    universes = APIClient.get_all_universes()
    if not universes:
        st.warning("No universes available.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Feed 1")
        feed1 = select_feed(1, universes)

    with col2:
        st.subheader("Feed 2")
        feed2 = select_feed(2, universes)
 

    # Initialize time window in session state if not present
    if "correlation_time_window" not in st.session_state:
        st.session_state.correlation_time_window = TIME_WINDOW_DAY

    def on_correlation_time_change():
        # Get the value directly from the widget key
        st.session_state.correlation_time_window = st.session_state.correlation_time_selector
        # Force a refresh of data
        st.cache_data.clear()

    # Use selectbox with on_change callback
    st.selectbox(
        "Select Time Window:",
        TIME_WINDOW_OPTIONS,
        index=TIME_WINDOW_OPTIONS.index(st.session_state.correlation_time_window),
        key="correlation_time_selector",
        on_change=on_correlation_time_change,
    )

    # Get time window from session state
    time_window = st.session_state.correlation_time_window

    if st.button("Generate Correlation Plot", type="primary", use_container_width=True):
        if feed1 and feed2:
            with st.spinner("Generating plot..."):
                # Use timestamp to ensure unique keys for plots
                timestamp = pd.Timestamp.now().isoformat()
                df1, df2 = get_correlation_data(feed1, feed2, time_window)
                if df1 is not None and df2 is not None:
                    fig = create_dual_axis_plot(feed1, feed2, df1, df2)
                    corr_value = calculate_correlation(df1, df2)

                    st.plotly_chart(fig, use_container_width=True, key=f"corr_plot_{timestamp}")
                    if corr_value is not None:
                        st.metric(
                            "Pearson Correlation Coefficient", f"{corr_value:.4f}", key=f"corr_metric_{timestamp}"
                        )
                else:
                    st.warning("Unable to generate plot. Check data availability.")
        else:
            st.warning("Select two complete feeds.")


def select_feed(index, universes):
    prefix = f"feed{index}_"

    selected_universe = st.selectbox("Universe:", [u["universe_name"] for u in universes], key=f"{prefix}universe")

    feed_data = APIClient.get_feed_from_db(universe_name=selected_universe)
    if feed_data.empty:
        st.warning(f"No data for universe {selected_universe}")
        return None

    selected_topic = st.selectbox("Topic:", feed_data["topic"].unique(), key=f"{prefix}topic")
    topic_data = feed_data[feed_data["topic"] == selected_topic]

    selected_source = st.selectbox("Source:", topic_data["source"].unique(), key=f"{prefix}source")
    source_data = topic_data[topic_data["source"] == selected_source]

    selected_feature = st.selectbox("Feature:", source_data["feature_name"].unique(), key=f"{prefix}feature")

    return {
        "universe_name": selected_universe,
        "topic": selected_topic,
        "source": selected_source,
        "feature_name": selected_feature,
        "display_name": f"{selected_universe}: {selected_topic} - {selected_feature} ({selected_source})",
    }


def get_correlation_data(feed1, feed2, time_window):
    # Create copies of feed dictionaries without display_name
    feed1_params = {k: v for k, v in feed1.items() if k != "display_name"}
    feed2_params = {k: v for k, v in feed2.items() if k != "display_name"}

    df1 = APIClient.get_feed_from_db(**feed1_params)
    df2 = APIClient.get_feed_from_db(**feed2_params)

    df1 = filter_dataframe_by_time(df1, time_window)
    df2 = filter_dataframe_by_time(df2, time_window)

    if df1.empty or df2.empty:
        return None, None

    df1["feature_value"] = pd.to_numeric(df1["feature_value"], errors="coerce")
    df2["feature_value"] = pd.to_numeric(df2["feature_value"], errors="coerce")

    df1.dropna(inplace=True)
    df2.dropna(inplace=True)

    df1.sort_values("created_timestamp", inplace=True)
    df2.sort_values("created_timestamp", inplace=True)

    return df1, df2


def create_dual_axis_plot(feed1, feed2, df1, df2):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df1["created_timestamp"], y=df1["feature_value"], name=feed1["display_name"], line=dict(color="blue")
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df2["created_timestamp"], y=df2["feature_value"], name=feed2["display_name"], line=dict(color="red")
        ),
        secondary_y=True,
    )

    fig.update_layout(title_text="Correlation Analysis", hovermode="x unified")
    fig.update_xaxes(title_text="Date & Time")
    fig.update_yaxes(title_text=feed1["feature_name"], secondary_y=False)
    fig.update_yaxes(title_text=feed2["feature_name"], secondary_y=True)

    return fig


def calculate_correlation(df1, df2):
    combined = pd.merge(df1, df2, on="created_timestamp", suffixes=("_1", "_2")).dropna()
    if len(combined) < 2:
        return None
    return combined["feature_value_1"].corr(combined["feature_value_2"])
