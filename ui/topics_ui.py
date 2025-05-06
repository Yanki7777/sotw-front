import streamlit as st
import pandas as pd
from utils.plot_utils import create_one_feature_plot
from utils.api_client import APIClient
from utils.time_utils import filter_dataframe_by_time, TIME_WINDOW_OPTIONS, TIME_WINDOW_DAY


def fetch_data(universe_name):
    return APIClient.get_feed_from_db(universe_name=universe_name)


def display_summary(topic_data):
    if topic_data.empty:
        return "No data available"
    return " | ".join(f"{len(df)} {src}" for src, df in topic_data.groupby('source'))


def topic_display_name(universe, topic):
    desc = APIClient.get_topic_description(universe, topic)
    return f"{topic} ({desc})" if desc else topic


def plot_features(universe_name, source, topic, features, time_window, displayed_features, display_name):
    for feature in features:
        feature_key = f"{source}:{feature}"
        if feature_key not in displayed_features:
            fig, plot_key = create_one_feature_plot(universe_name, source, topic, feature, time_window)
            if fig:
                st.subheader(f"{display_name} - {feature}")
                st.plotly_chart(fig, use_container_width=True, key=plot_key)
                displayed_features.add(feature_key)
            else:
                st.info(f"No {feature} data available for {topic} from {source}")


def display_topic(universe):
    universe_name = universe.get("universe_name")
    all_feed_data = fetch_data(universe_name)

    if all_feed_data.empty:
        st.warning("No data available for analysis. Please collect price and feed data.")
        return

    available_topics = sorted(all_feed_data["topic"].unique())

    header_col, refresh_col, summary_col = st.columns([1.5, 0.2, 3.3])
    header_col.header("🔍 Topic Dashboard")

    if refresh_col.button("🔄", help="Refresh data"):
        st.cache_data.clear()
        st.rerun()

    display_topics = {topic_display_name(universe, t): t for t in available_topics}
    selected_display_topic = st.selectbox("Select topic:", options=list(display_topics.keys()))
    selected_topic = display_topics[selected_display_topic]

    topic_data = all_feed_data[all_feed_data["topic"] == selected_topic]
    summary_col.caption(f"<span style='font-size:15px;'>{display_summary(topic_data)}</span>", unsafe_allow_html=True)

    time_window = st.selectbox("Time Window:", TIME_WINDOW_OPTIONS, index=TIME_WINDOW_OPTIONS.index(TIME_WINDOW_DAY))

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
                    universe_name,
                    row["source"],
                    selected_topic,
                    [row["feature_name"]],
                    time_window,
                    displayed_features,
                    selected_display_topic
                )

    for source, df in topic_data.groupby("source"):
        with st.expander(f"{source.upper()} Data", expanded=True):
            plot_features(
                universe_name,
                source,
                selected_topic,
                df["feature_name"].unique(),
                time_window,
                displayed_features,
                selected_display_topic
            )

    with st.expander("View Raw Data"):
        raw_data = filter_dataframe_by_time(topic_data, time_window).sort_values("original_timestamp", ascending=False)
        st.dataframe(raw_data, use_container_width=True, height=300)
