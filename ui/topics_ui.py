import streamlit as st
import pandas as pd
from utils.plot_utils import create_one_feature_plot
from utils.api_client import APIClient
from utils.time_utils import filter_dataframe_by_time, TIME_WINDOW_OPTIONS, TIME_WINDOW_DAY


def fetch_data(universe):
    return APIClient.get_feed_from_db(universe_name=universe.get("universe_name"))


def display_summary(topic_data):
    if topic_data.empty:
        return "No data available"
    summary = [f"{len(df)} {src}" for src, df in topic_data.groupby('source')]
    return " | ".join(summary)


def topic_display_name(universe, topic):
    desc = APIClient.get_topic_description(universe, topic)
    return f"{topic} ({desc})" if desc else topic


def plot_features(universe, source, topic, features, time_param, displayed_features):
    universe_name = universe["universe_name"]
    for feature in features:
        feature_key = f"{source}:{feature}"
        if feature_key not in displayed_features:
            fig, plot_key = create_one_feature_plot(universe_name, source, topic, feature, time_param)
            if fig:
                st.subheader(f"{topic_display_name(universe, topic)} - {feature}")
                st.plotly_chart(fig, use_container_width=True, key=plot_key)
                displayed_features.add(feature_key)
            else:
                st.info(f"No {feature} data available for {topic} from {source}")



def display_topic(universe):
    all_feed_data = fetch_data(universe)
    available_topics = sorted(all_feed_data["topic"].unique()) if not all_feed_data.empty else []

    with st.container():
        header_col, refresh_col, summary_col = st.columns([1.5, 0.2, 3.3])
        header_col.header("🔍 Topic Dashboard")

        def refresh_data():
            st.cache_data.clear()
            st.session_state["topic_data_refreshed"] = True

        refresh_col.button("🔄", help="Refresh data", key="topic_refresh_button", on_click=refresh_data)

        selected_topic = st.session_state.get("selected_topic", available_topics[0] if available_topics else None)
        topic_data = all_feed_data[all_feed_data["topic"] == selected_topic]

        summary_col.caption(f"<span style='font-size:15px;'>{display_summary(topic_data)}</span>", unsafe_allow_html=True)

        if not available_topics:
            st.warning("No data available for analysis. Please collect price and feed data.")
            return

        display_topics = {topic_display_name(universe, t): t for t in available_topics}
        selected_display_topic = st.selectbox("Select topic:", options=list(display_topics.keys()))
        selected_topic = display_topics[selected_display_topic]
        st.session_state.selected_topic = selected_topic

        time_param = st.selectbox("Time Window:", TIME_WINDOW_OPTIONS, index=TIME_WINDOW_OPTIONS.index(st.session_state.get("topic_time_window", TIME_WINDOW_DAY)))
        st.session_state.topic_time_window = time_param

        if topic_data.empty:
            st.warning(f"No feed data available for {selected_display_topic}. Try another topic.")
            return

        displayed_features = set()

        if "feature_is_target" in topic_data:
            targets = topic_data[topic_data["feature_is_target"]].drop_duplicates(["source", "feature_name"])
            if not targets.empty:
                st.subheader(f"Target Variables for {selected_display_topic}")
                for _, row in targets.iterrows():
                    plot_features(
                        universe,
                        row["source"],
                        selected_topic,
                        [row["feature_name"]],
                        time_param,
                        displayed_features
                    )


        grouped = topic_data.groupby("source")
        for source, df in grouped:
            with st.expander(f"{source.upper()} Data", expanded=True):
                plot_features(universe, source, selected_topic, df["feature_name"].unique(), time_param, displayed_features)


        with st.expander("View Raw Data", expanded=False):
            raw_data = filter_dataframe_by_time(topic_data, time_param).sort_values("original_timestamp", ascending=False)
            st.dataframe(raw_data, use_container_width=True, height=300)
