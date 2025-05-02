"""Component for displaying topic analysis dashboard in Streamlit."""

import streamlit as st
import pandas as pd
from utils.plot_utils import create_one_feature_plot
from utils.api_client import APIClient
from utils.time_utils import filter_dataframe_by_time, TIME_WINDOW_OPTIONS, TIME_WINDOW_DAY


def get_feature_names_for_source(df, source):
    """Get unique feature names for a specific source in the dataframe."""
    if df is None or df.empty:
        return []
    return df[df["source"] == source]["feature_name"].unique().tolist()


def display_topic(universe):
    # Use a container to isolate this component
    topic_container = st.container()

    # ---- prepare data ----
    all_feed_data = APIClient.get_feed_from_db(universe_name=universe.get("universe_name"))
    available_topics = sorted(all_feed_data["topic"].unique().tolist()) if all_feed_data is not None else []

    def topic_display_name(topic):
        desc = APIClient.get_topic_description(universe, topic)
        if desc:
            return f"{topic} ({desc})"
        return topic

    ## ---- UI ----
    with topic_container:
        if st.session_state.get("refresh_topic_dashboard", False):
            st.session_state["refresh_topic_dashboard"] = False
            # Create a container-specific rerun indicator instead of a full page rerun
            st.session_state["topic_data_refreshed"] = True

        # Render header, refresh button, and data summary all in one line
        header_col, refresh_col, summary_col = st.columns([1.5, 0.2, 3.3])

        with header_col:
            st.header("🔍 Topic Analysis Dashboard")

        with refresh_col:

            def refresh_data():
                # Clear cache but don't trigger full page rerun
                st.cache_data.clear()
                st.session_state["topic_data_refreshed"] = True

            st.button("🔄", help="Refresh data", key="topic_refresh_button", on_click=refresh_data)

        with summary_col:
            selected_topic = st.session_state.get(
                "selected_topic",
                "AAPL" if "AAPL" in available_topics else (available_topics[0] if available_topics else None),
            )
            topic_data = (
                all_feed_data[all_feed_data["topic"] == selected_topic]
                if all_feed_data is not None and selected_topic is not None
                else pd.DataFrame()
            )
            data_points = []
            # Get unique sources dynamically from the data
            sources = topic_data["source"].unique().tolist() if not topic_data.empty else []
            for source in sources:
                source_data = topic_data[topic_data["source"] == source] if not topic_data.empty else pd.DataFrame()
                if not source_data.empty:
                    source_count = len(source_data)
                    data_points.append(f"{source_count} {source}")
            data_summary = " | ".join(data_points) if data_points else "No data available"
            st.caption(f"<span style='font-size:15px;'>{data_summary}</span>", unsafe_allow_html=True)

        st.markdown(
            """
        <style>
        .stSelectbox, .stSelectbox > div > label, .stButton, .stWarning, .stCaption, .stInfo, .stExpander {
            font-size: 1.1rem !important;
        }
        h1, h2, h3 {
            font-size: 1.8rem !important;
        }
        .stDataFrame {
            font-size: 1.05rem !important;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Map available_topics to display names for selectbox
        topic_display_map = {topic: topic_display_name(topic) for topic in available_topics}
        display_to_topic = {v: k for k, v in topic_display_map.items()}
        available_display_topics = [topic_display_map[t] for t in available_topics]

        if not available_display_topics:
            st.warning("No data available for analysis. Please make sure you've collected price and feed data.")
            return

        # Initialize topic selection in session state if not present
        if "selected_topic" not in st.session_state:
            default_topic = (
                "AAPL" if "AAPL" in available_topics else (available_topics[0] if available_topics else None)
            )
            st.session_state.selected_topic = default_topic

        selected_topic = st.session_state.selected_topic
        if selected_topic not in available_topics and available_topics:
            selected_topic = available_topics[0]
            st.session_state.selected_topic = selected_topic

        # Use display name for selectbox
        selected_display_topic = topic_display_map.get(selected_topic, available_display_topics[0])

        col1, col2 = st.columns([2, 4])

        with col1:
            # Use on_change instead of a key to avoid triggering reruns
            prev_selected_topic = st.session_state.selected_topic
            selected_display_topic = st.selectbox(
                "Select topic:",
                options=available_display_topics,
                index=available_display_topics.index(selected_display_topic)
                if selected_display_topic in available_display_topics
                else 0,
                key="selected_topic_display",
            )
            if display_to_topic[selected_display_topic] != prev_selected_topic:
                st.session_state.selected_topic = display_to_topic[selected_display_topic]
            selected_topic = st.session_state.selected_topic

        with col2:
            time_col = st.columns([1])[0]

            with time_col:
                # Initialize time window if not in session state
                if "topic_time_window" not in st.session_state:
                    st.session_state.topic_time_window = TIME_WINDOW_DAY

                def on_topic_time_window_change():
                    # Get the value directly from the widget key
                    st.session_state.topic_time_window = st.session_state.topic_analysis_time_selector
                    # Force a refresh when time window changes
                    st.cache_data.clear()
                    st.session_state["topic_data_refreshed"] = True

                st.selectbox(
                    "Time Window:",
                    TIME_WINDOW_OPTIONS,
                    index=TIME_WINDOW_OPTIONS.index(st.session_state.topic_time_window),
                    key="topic_analysis_time_selector",
                    on_change=on_topic_time_window_change,
                )

        time_param = st.session_state.topic_time_window  # Use session state value directly

        if all_feed_data is None or all_feed_data.empty:
            st.warning("No feed data available. Please make sure you've collected data.")
            return

        topic_feed_data = all_feed_data[all_feed_data["topic"] == selected_topic]

        if topic_feed_data.empty:
            st.warning(f"No feed data available for {topic_display_name(selected_topic)}. Please try another topic.")
            return

        displayed_features = set()

        if "feature_is_target" in topic_feed_data.columns:
            target_features = topic_feed_data[topic_feed_data["feature_is_target"]]
            if not target_features.empty:
                st.subheader(f"Target Variables for {topic_display_name(selected_topic)}")
                for _, row in target_features.drop_duplicates(["source", "feature_name"]).iterrows():
                    source = row["source"]
                    feature_name = row["feature_name"]
                    feature_key = f"{source}:{feature_name}"
                    try:
                        # Use timestamp to ensure unique plot keys
                        timestamp = pd.Timestamp.now().isoformat()
                        feature_plot_result = create_one_feature_plot(
                            universe.get("universe_name"), source, selected_topic, feature_name, time_param
                        )
                        if isinstance(feature_plot_result, tuple) and len(feature_plot_result) == 2:
                            target_fig, plot_key = feature_plot_result
                        else:
                            target_fig = feature_plot_result
                            plot_key = f"{source}_{selected_topic}_{feature_name}_{time_param}_{timestamp}"
                        if target_fig is not None:
                            st.plotly_chart(target_fig, use_container_width=True, key=plot_key)
                            displayed_features.add(feature_key)
                        else:
                            st.info(
                                f"No data available for target feature {feature_name} from {source} for {topic_display_name(selected_topic)}"
                            )
                    except Exception as e:
                        st.error(f"Error plotting {feature_name} from {source}: {str(e)}")

        source_features = (
            topic_feed_data.groupby(["source", "feature_name"]).size().reset_index()[["source", "feature_name"]]
        )
        sources = sorted(source_features["source"].unique())

        for source in sources:
            with st.expander(f"{source.upper()} Data", expanded=True):
                features = source_features[source_features["source"] == source]["feature_name"].unique()
                for feature in features:
                    feature_key = f"{source}:{feature}"
                    if feature_key in displayed_features:
                        continue
                    st.subheader(f"{topic_display_name(selected_topic)} - {feature}")
                    try:
                        # Use timestamp to ensure unique plot keys
                        timestamp = pd.Timestamp.now().isoformat()
                        feature_plot_result = create_one_feature_plot(
                            universe.get("universe_name"), source, selected_topic, feature, time_param
                        )
                        if isinstance(feature_plot_result, tuple) and len(feature_plot_result) == 2:
                            feature_fig, plot_key = feature_plot_result
                        else:
                            feature_fig = feature_plot_result
                            plot_key = f"{source}_{selected_topic}_{feature}_{time_param}_{timestamp}"
                        if feature_fig is not None:
                            st.plotly_chart(feature_fig, use_container_width=True, key=plot_key)
                            displayed_features.add(feature_key)
                        else:
                            st.info(
                                f"No {feature} data available for {topic_display_name(selected_topic)} from {source}"
                            )
                    except Exception as e:
                        st.error(f"Error plotting {feature} from {source}: {str(e)}")

        with st.expander("View Raw Data", expanded=False):
            if all_feed_data is not None and not all_feed_data.empty:
                topic_data = all_feed_data[all_feed_data["topic"] == selected_topic]
                if not topic_data.empty:
                    if time_param != "all":
                        topic_data = filter_dataframe_by_time(topic_data, time_param)
                    topic_data = topic_data.sort_values("original_timestamp", ascending=False)
                    st.dataframe(topic_data, use_container_width=True, height=300)
                else:
                    st.info(f"No raw data available for {topic_display_name(selected_topic)}")
            else:
                st.info("No raw data available")
