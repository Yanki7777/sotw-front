"""UI component for displaying features"""

import streamlit as st
import pandas as pd
from utils.plot_utils import create_one_feature_plot
from utils.api_client import APIClient
from utils.time_utils import TIME_WINDOW_OPTIONS, TIME_WINDOW_ALL


def display_universe(universe):
    st.header(f"📈 {universe.get('universe_name')} Universe")

    sources, features_by_source = get_available_sources(universe)
    
    if not sources:
        st.warning("No feed data available. Please generate some data first.")
        return
    
    # Directly use widget keys for managing selections
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        selected_source = st.selectbox(
            "Data Source:",
            sources,
            key="selected_source"
        )

    available_features = features_by_source.get(selected_source, [])
    
    with col2:
        selected_feature = st.selectbox(
            "Feature:",
            available_features if available_features else ["No features available"],
            key=f"selected_feature_{selected_source}",  # unique per source
            disabled=not available_features
        )

    with col3:
        time_window = st.selectbox(
            "Time Window:",
            TIME_WINDOW_OPTIONS,
            key="selected_time_window"
        )

    # Fetch and display last updated timestamp directly
    if available_features and selected_feature != "No features available":
        last_update = APIClient.get_latest_feed_timestamp(
            source=selected_source,
            feature_name=selected_feature,
            universe_name=universe.get("universe_name"),
        )
        if last_update:
            ts = pd.to_datetime(last_update)
            st.caption(f"Last updated: {ts.strftime('%Y-%m-%d %H:%M:%S')}" if pd.notnull(ts) else "Last updated: N/A")

        display_universe_plot(universe.get("universe_name"), selected_source, selected_feature, time_window)
    else:
        st.info("Please select a valid data source and feature to view the data.")


def get_available_sources(universe):
    """Get available sources and their features from feed data"""
    try:
        df = APIClient.get_feed_from_db(universe_name=universe.get("universe_name"))
        if df is None or df.empty:
            return [], {}
        sources = sorted(df["source"].unique().tolist())
        features_by_source = {
            source: sorted(df[df["source"] == source]["feature_name"].unique().tolist()) for source in sources
        }
        return sources, features_by_source
    except Exception as e:
        print(f"Error getting available options: {e}")
        return [], {}


def display_universe_plot(universe_name, selected_source, selected_feature, time_window):
    source_display = selected_source
    feature_display = selected_feature

    # Get the universe object (from session or fallback to None)
    universe = None
    if "universes" in st.session_state:
        universe = next((u for u in st.session_state["universes"] if u.get("universe_name") == universe_name), None)

    # Use get_topic_description to get the description for the selected feature
    if universe and selected_feature:
        desc = APIClient.get_topic_description(universe, selected_feature)
        if desc:
            topic_display = f"{selected_feature} ({desc})"
        else:
            topic_display = selected_feature
    else:
        topic_display = feature_display

    with st.spinner(f"Loading {feature_display} data from {source_display}..."):
        # Ensure we're using the current time window from session state
        current_time_window = st.session_state.universe_time_window
        feature_plot_result = create_one_feature_plot(
            universe_name,
            selected_source,
            None,
            selected_feature,
            current_time_window,  # Use the session state value
        )
        if isinstance(feature_plot_result, tuple) and len(feature_plot_result) == 2:
            feature_plot, plot_key = feature_plot_result
        else:
            feature_plot = feature_plot_result
            # Add timestamp to ensure plot key is always unique when time window changes
            timestamp = pd.Timestamp.now().isoformat()
            plot_key = f"{selected_source}_all_{selected_feature}_{current_time_window}_{timestamp}"

        if feature_plot is not None:
            st.plotly_chart(feature_plot, use_container_width=True, key=plot_key)
        else:
            display_name = topic_display if topic_display else feature_display
            st.warning(
                f"No data available for {display_name} from {source_display} for {current_time_window}."
                if current_time_window != TIME_WINDOW_ALL
                else f"No data available for {display_name} from {source_display}."
            )


def source_changed():
    """Reset feature selection when source changes"""
    st.session_state.universe_selected_feature = None
