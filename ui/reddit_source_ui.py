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
        (
            sentiment_scores,
            topic_sentiments,
            num_submissions,
            num_comments,
            last_timestamps,
            topic_averages,
            overall_sentiment_average,
        ) = APIClient.create_reddit_feed(universe)

        print(
            f"REDDIT source data summary: {len(sentiment_scores)} data points analyzed across {len(topic_sentiments)} topics"
        )

    # Store results in a dictionary
    results = {
        "sentiment_scores": sentiment_scores,
        "topic_sentiments": topic_sentiments,
        "num_submissions": num_submissions,
        "num_comments": num_comments,
        "last_timestamps": last_timestamps,
        "topic_averages": topic_averages,
        "overall_sentiment_average": overall_sentiment_average,
    }

    st.markdown("---")
    st.header("Reddit Sentiment source")

    # Show analysis scope information
    st.caption(f"Analyzed Reddit posts tracking {len(results.get('topic_sentiments', {}))} topics")

    tab1, tab2, tab3 = st.tabs(["Overall Sentiment", "topic Sentiment", "Summary Statistics"])

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

    if avg is not None:
        avg_color = determine_sentiment_color(avg)
        st.markdown(
            f"<h3>Average topic Sentiment: <span style='color:{avg_color}'>{avg:.3f}</span></h3>",
            unsafe_allow_html=True,
        )
        st.progress(avg / 2 + 0.5)

    fig = create_reddit_source_sentiment_plot(
        results["sentiment_scores"], results["num_submissions"], results["num_comments"]
    )
    st.plotly_chart(fig, use_container_width=True)


def display_topic_sentiment(results):
    """Display topic-specific sentiment analysis."""
    st.header("Topic-Specific Sentiment")
    figs = create_reddit_source_topic_plot(
        results["topic_sentiments"], results["num_submissions"], results["num_comments"]
    )
    for topic, fig in figs.items():
        st.subheader(f"{topic.upper()} Sentiment")

        last_timestamp = results["last_timestamps"].get(topic)
        if last_timestamp:
            try:
                # Convert string to datetime object
                last_timestamp = datetime.fromisoformat(last_timestamp)
                formatted_timestamp = last_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                st.caption(f"Last mentioned: {formatted_timestamp}")
            except ValueError:
                st.caption("Last mentioned: Invalid date format")
        else:
            st.caption("No mentions found")

        st.plotly_chart(fig, use_container_width=True)


def display_summary_statistics(results):
    """Display summary statistics of the analysis."""
    st.header("Summary Statistics")
    total_submissions = sum(results["num_submissions"].values())
    total_comments = sum(results["num_comments"].values())
    subreddit_count = len(results.get("subreddits", []))
    positive_karma_filter = results.get("positive_karma_only", False)

    st.subheader("Overall Data")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Subreddits Scanned", subreddit_count)
    col2.metric("Total Submissions", total_submissions)
    col3.metric("Total Comments", total_comments)
    col4.metric("Total Data Points", len(results["sentiment_scores"]))

    st.markdown(f"**Filter Settings**: Positive Karma Only: {'✅ Yes' if positive_karma_filter else '❌ No'}")

    st.subheader("topic Analysis")
    for topic, scores in results["topic_sentiments"].items():
        if scores:
            avg_score = np.mean(scores)
            avg_color = determine_sentiment_color(avg_score)
            timestamp_info = format_timestamp(results["last_timestamps"].get(topic))
            st.markdown(
                f"**{topic.upper()}**: {len(scores)} mentions, Avg Sentiment: <b style='color:{avg_color}'>{avg_score:.3f}</b>{timestamp_info}",
                unsafe_allow_html=True,
            )
            st.progress(avg_score / 2 + 0.5)


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
        try:
            dt_timestamp = datetime.fromisoformat(timestamp)
            return f" | Last Mention: {dt_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        except ValueError:
            return " | Last Mention: Invalid date format"
    return ""
