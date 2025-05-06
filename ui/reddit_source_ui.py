"""Results display module for the Reddit Sentiment Analysis app."""

import streamlit as st
import numpy as np
from datetime import datetime
from utils.plot_utils import create_reddit_source_sentiment_plot, create_reddit_source_topic_plot
from utils.api_client import APIClient
from config import (
    NEGATIVE_SENTIMENT_THRESHOLD,
    POSITIVE_SENTIMENT_THRESHOLD,
    SENTIMENT_COLORS,
)


def display_reddit_source(universe):
    if not universe:
        st.warning("No universe selected.")
        return

    with st.spinner(f"Scanning REDDIT and analyzing for {universe.get('universe_name')}..."):
        universe_feeds, overall_sentiment_average = APIClient.create_reddit_feed(universe)

        print(f"REDDIT source data summary: Analyzed {len(universe_feeds)} topics")

    results = {
        "universe_feeds": universe_feeds,
        "overall_sentiment_average": overall_sentiment_average,
    }

    st.markdown("---")
    st.header("Reddit Sentiment Source")

    st.caption(f"Analyzed Reddit posts tracking {len(results['universe_feeds'])} topics")

    tab1, tab2, tab3 = st.tabs(["Overall Sentiment", "Topic Sentiment", "Summary Statistics"])

    with tab1:
        display_overall_sentiment(results)
    with tab2:
        display_topic_sentiment(results)
    with tab3:
        display_summary_statistics(results)


def display_overall_sentiment(results):
    """Display overall sentiment analysis."""
    st.header("Overall Sentiment Analysis")
    avg = results["overall_sentiment_average"]

    avg_color = determine_sentiment_color(avg)
    st.markdown(
        f"<h3>Average Sentiment: <span style='color:{avg_color}'>{avg:.3f}</span></h3>",
        unsafe_allow_html=True,
    )
    st.progress(avg / 2 + 0.5)

    sentiment_scores = [feed["sentiment_average"] for feed in results["universe_feeds"]]
    total_submissions = sum(feed["num_submissions"] for feed in results["universe_feeds"])
    total_comments = sum(feed["num_comments"] for feed in results["universe_feeds"])

    fig = create_reddit_source_sentiment_plot(sentiment_scores, total_submissions, total_comments)
    st.plotly_chart(fig, use_container_width=True)


def display_topic_sentiment(results):
    """Display topic-specific sentiment analysis."""
    st.header("Topic-Specific Sentiment")
    topic_sentiments = {feed["topic"]: feed["sentiment_average"] for feed in results["universe_feeds"]}
    num_submissions = {feed["topic"]: feed["num_submissions"] for feed in results["universe_feeds"]}
    num_comments = {feed["topic"]: feed["num_comments"] for feed in results["universe_feeds"]}
    figs = create_reddit_source_topic_plot(topic_sentiments, num_submissions, num_comments)

    for feed in results["universe_feeds"]:
        topic = feed["topic"]
        avg_sentiment = feed["sentiment_average"]
        last_timestamp = feed["last_timestamp"]

        avg_color = determine_sentiment_color(avg_sentiment)
        st.subheader(f"{topic.upper()} Sentiment")

        if last_timestamp:
            formatted_timestamp = last_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"Last mentioned: {formatted_timestamp}")
        else:
            st.caption("No mentions found")

        st.markdown(
            f"Average Sentiment: <b style='color:{avg_color}'>{avg_sentiment:.3f}</b>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(figs[topic], use_container_width=True)


def display_summary_statistics(results):
    """Display summary statistics of the analysis."""
    st.header("Summary Statistics")
    total_submissions = sum(feed["num_submissions"] for feed in results["universe_feeds"])
    total_comments = sum(feed["num_comments"] for feed in results["universe_feeds"])
    total_topics = len(results["universe_feeds"])

    st.subheader("Overall Data")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Topics", total_topics)
    col2.metric("Total Submissions", total_submissions)
    col3.metric("Total Comments", total_comments)

    st.subheader("Topic Analysis")
    for feed in results["universe_feeds"]:
        topic = feed["topic"]
        avg_sentiment = feed["sentiment_average"]
        avg_color = determine_sentiment_color(avg_sentiment)
        last_timestamp = feed["last_timestamp"]

        timestamp_info = format_timestamp(last_timestamp)

        st.markdown(
            f"**{topic.upper()}**: Avg Sentiment: <b style='color:{avg_color}'>{avg_sentiment:.3f}</b>{timestamp_info}",
            unsafe_allow_html=True,
        )
        st.progress(avg_sentiment / 2 + 0.5)


def determine_sentiment_color(score):
    """Determine the color based on sentiment score."""
    if score < NEGATIVE_SENTIMENT_THRESHOLD:
        return SENTIMENT_COLORS["negative"]
    elif score > POSITIVE_SENTIMENT_THRESHOLD:
        return SENTIMENT_COLORS["positive"]
    return SENTIMENT_COLORS["neutral"]


def format_timestamp(timestamp):
    """Format the timestamp for display."""
    if timestamp:
        return f" | Last Mention: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    return ""
