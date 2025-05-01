"""UI component for displaying features"""

import streamlit as st
import pandas as pd
from datetime import datetime
from plot_utils import create_one_feature_plot
from api_client import APIClient


def filter_feed_by_time(df, time_param):
    """Filter the feed dataframe by the specified time window"""
    if df is None or df.empty:
        return None

    if time_param == "all":
        return df

    now = datetime.now()

    if time_param == "hour":
        cutoff = now - pd.Timedelta(hours=1)
    elif time_param == "day":
        cutoff = now - pd.Timedelta(days=1)
    elif time_param == "week":
        cutoff = now - pd.Timedelta(weeks=1)
    elif time_param == "month":
        cutoff = now - pd.Timedelta(days=30)
    else:
        return df

    return df[df["created_timestamp"] >= cutoff]


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


def display_universe_plot(universe_name, selected_source, selected_feature, time_param, time_window):
    print(f"Selected source: {selected_source}, feature: {selected_feature}, time_param: {time_param}")
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
        feature_plot_result = create_one_feature_plot(
            universe_name,
            selected_source,
            None,
            selected_feature,
            time_param,
        )
        if isinstance(feature_plot_result, tuple) and len(feature_plot_result) == 2:
            feature_plot, plot_key = feature_plot_result
        else:
            feature_plot = feature_plot_result
            plot_key = f"{selected_source}_all_{selected_feature}_{time_param}"

        if feature_plot is not None:
            st.plotly_chart(feature_plot, use_container_width=True, key=plot_key)
        else:
            display_name = topic_display if topic_display else feature_display
            st.warning(
                f"No data available for {display_name} from {source_display} for {time_window.lower()}."
                if time_window != "All Time"
                else f"No data available for {display_name} from {source_display}."
            )


def display_universe(universe):
    # Use a container to isolate this component
    universe_container = st.container()

    with universe_container:
        if st.session_state.get("refresh_universe_dashboard", False):
            st.session_state["refresh_universe_dashboard"] = False
            # Create a container-specific rerun indicator instead of a full page rerun
            st.session_state["universe_data_refreshed"] = True

        header_col, updated_col, refresh_col = st.columns([2, 2, 2])
        with header_col:
            st.header(f"📈 {universe.get('universe_name')} Universe")

        sources, features_by_source = get_available_sources(universe)

        if not sources:
            st.warning("No feed data available. Please generate some data first.")
            return

        st.markdown(
            """
        <style>
        .stSelectbox, .stSelectbox > div > label, .stButton, .stWarning, .stCaption, .stInfo {
            font-size: 1.1rem !important;
        }
        h1, h2, h3 {
            font-size: 1.8rem !important;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Initialize selections in session state
        if "universe_selected_source" not in st.session_state:
            st.session_state.universe_selected_source = sources[0] if sources else None

        if "universe_selected_feature" not in st.session_state:
            features = features_by_source.get(st.session_state.universe_selected_source, [])
            st.session_state.universe_selected_feature = features[0] if features else None

        if "universe_time_window" not in st.session_state:
            st.session_state.universe_time_window = "All Time"

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            selected_source = st.selectbox(
                "Data Source:",
                sources,
                index=sources.index(st.session_state.universe_selected_source)
                if st.session_state.universe_selected_source in sources
                else 0,
                key="feature_source_selector",
                on_change=lambda: source_changed(),
            )
            st.session_state.universe_selected_source = selected_source

        available_features = features_by_source.get(selected_source, [])

        with col2:
            default_index = 0
            if st.session_state.universe_selected_feature in available_features:
                default_index = available_features.index(st.session_state.universe_selected_feature)

            selected_feature = st.selectbox(
                "Feature:",
                available_features if available_features else ["No features available"],
                index=default_index,
                key="feature_name_selector",
                disabled=not available_features,
            )
            st.session_state.universe_selected_feature = selected_feature

        with col3:
            time_options = ["All Time", "Last Hour", "Last Day", "Last Week", "Last Month"]
            time_window = st.selectbox(
                "Time Window:",
                time_options,
                index=time_options.index(st.session_state.universe_time_window),
                key="feature_time_selector",
            )
            st.session_state.universe_time_window = time_window

        time_param = {"Last Hour": "hour", "Last Day": "day", "Last Week": "week", "Last Month": "month"}.get(
            time_window, "all"
        )

        last_update = None
        if available_features and selected_feature != "No features available":
            last_update = APIClient.get_latest_feed_timestamp(
                source=selected_source,
                feature_name=selected_feature,
                universe_name=universe.get("universe_name"),
            )
        with updated_col:
            if last_update:
                ts = pd.to_datetime(last_update)
                if pd.notnull(ts):
                    st.caption(
                        f"<span style='font-size:15px;'>Last updated: {ts.strftime('%Y-%m-%d %H:%M:%S')}</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption(
                        "<span style='font-size:15px;'>Last updated: N/A</span>",
                        unsafe_allow_html=True,
                    )
        with refresh_col:

            def refresh_feed():
                st.cache_data.clear()
                st.session_state["universe_data_refreshed"] = True

            st.button("🔄 Refresh", help="Refresh feed data", key="universe_refresh_button", on_click=refresh_feed)

        if available_features and selected_feature != "No features available":
            display_universe_plot(
                universe.get("universe_name"), selected_source, selected_feature, time_param, time_window
            )
        else:
            st.info("Please select a data source and feature to view the data.")


def source_changed():
    """Reset feature selection when source changes"""
    st.session_state.universe_selected_feature = None
