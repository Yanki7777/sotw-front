"""UI component for displaying GNews news sentiment."""

import streamlit as st
import pandas as pd
from utils.api_client import APIClient


def display_gnews_source(universe):
    if not universe:
        st.warning("No universe selected.")
        return

    with st.spinner(f"Fetching news for {len(universe.get('topics'))} topic(s)..."):
        universe_feeds, overall_sentiment_average = APIClient.create_gnews_feed(universe)

    print(f"GNEWS source data summary: {len(universe_feeds)} topics analyzed")

    if not universe_feeds:
        st.warning("No news data found for the selected topics.")
        return

    st.header("GNews Sentiment Analysis")

    # Display overall sentiment
    sentiment_color = "green" if overall_sentiment_average > 0 else "red" if overall_sentiment_average < 0 else "black"
    st.markdown(
        f"<h3 style='color:{sentiment_color}'>Overall Market Sentiment: {overall_sentiment_average:.4f}</h3>",
        unsafe_allow_html=True,
    )

    topic_data = []
    for feed in universe_feeds:
        latest_date = feed["latest_article"]["published date"] if feed["latest_article"] else ""
        topic_data.append(
            {
                "Topic": feed["topic"],
                "Vader Sentiment": feed["vader_sentiment"],    
                "Finbert Sentiment": feed["finbert_sentiment"],
                "Articles": feed["article_count"],
                "Latest Article": latest_date,
            }
        )

    if topic_data:
        df = pd.DataFrame(topic_data)
        st.subheader("GNews Topic Sentiment Scores")

        sentiment_cols = [ "Vader Sentiment", "Finbert Sentiment"] 

        st.write(
            df.style.format({col: "{:.4f}" for col in sentiment_cols})
            .applymap(
                lambda val: "color: green" if val > 0 else ("color: red" if val < 0 else "color: black"),
                subset=sentiment_cols,
            )
            .set_table_styles([{"selector": "th, td", "props": [("text-align", "left"), ("padding", "8px")]}])
            .to_html(),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.header("News Articles")

    for feed in universe_feeds:
        if not feed["news"]:
            continue

        st.subheader(f"{feed['topic'].upper()} ({feed['article_count']} articles)")

        for item in feed["news"]:
            col1, col2 = st.columns([1, 3])

            with col1:
                st.markdown(f"<h3>{feed['topic'].upper()}</h3>", unsafe_allow_html=True)

                sentiment_score = float(item.get("vader_sentiment", 0))
                sentiment_color = "green" if sentiment_score > 0 else "red" if sentiment_score < 0 else "black"

                st.markdown(
                    f"<h4 style='color:{sentiment_color}'><b>Vader Sentiment:</b> {sentiment_score:.2f}</h4>",
                    unsafe_allow_html=True,
                )
                sentiment_score = float(item.get("finbert_sentiment", 0))
                sentiment_color = "green" if sentiment_score > 0 else "red" if sentiment_score < 0 else "black"

                st.markdown(
                    f"<h4 style='color:{sentiment_color}'><b>Finbert Sentiment:</b> {sentiment_score:.2f}</h4>",
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(f"### {item.get('title', '')}")
                st.caption(f"Published: {item.get('published date', '')}")
                description = item.get("description", "")
                st.write(description[:500] + ("..." if len(description) > 500 else ""))

            st.divider()
