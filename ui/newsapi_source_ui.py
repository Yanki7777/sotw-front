"""UI component for displaying NewsAPI news sentiment."""

import streamlit as st
import pandas as pd
from utils.api_client import APIClient


def display_newsapi_source(universe):
    if not universe:
        st.warning("No universe selected.")
        return

    # Fetch news for all topics with UI feedback
    with st.spinner(f"Fetching news for {len(universe.get('topics'))} topic(s)..."):
        universe_feeds, overall_sentiment_average = APIClient.create_newsapi_feed(universe)

    print(
        f"NEWSAPI source data summary: {len(universe_feeds)} topics analyzed."
    )

    has_news = any(feed["articles"] for feed in universe_feeds)

    if not has_news:
        st.warning("No news data found for the selected topics.")
        st.info(
            "Check that your NEWSAPI_KEY is properly set in your .env file and that you have entered valid topic symbols."
        )
        return

    # Display overall sentiment average
    st.header("NewsAPI Sentiment Analysis")

    # Display overall sentiment with color
    if overall_sentiment_average > 0:
        st.markdown(
            f"<h3 style='color:green'>Overall Market Sentiment: {overall_sentiment_average:.4f}</h3>",
            unsafe_allow_html=True,
        )
    elif overall_sentiment_average < 0:
        st.markdown(
            f"<h3 style='color:red'>Overall Market Sentiment: {overall_sentiment_average:.4f}</h3>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<h3>Overall Market Sentiment: {overall_sentiment_average:.4f}</h3>",
            unsafe_allow_html=True,
        )

    # Create a dataframe to display individual topic sentiments
    topic_data = []
    for feed in universe_feeds:
        latest_date = feed["latest_article"]["published_date"] if feed["latest_article"] else ""

        topic_data.append(
            {
                "topic": feed["topic"],
                "Sentiment Score": feed["sentiment_average"],
                "Articles": feed["article_count"],
                "Latest Article": latest_date,
            }
        )

    if topic_data:
        df = pd.DataFrame(topic_data)
        st.subheader("NewsAPI Topic Sentiment Scores")

        # Use st.write with HTML for custom styling
        html = """
        <style>
            table.dataframe {
                font-size: 20px !important;
            }
            table.dataframe td, table.dataframe th {
                text-align: left !important;
                padding: 8px !important;
            }
        </style>
        """
        st.write(html, unsafe_allow_html=True)

        # Convert sentiment scores to colored HTML text
        def color_sentiment(val):
            color = "green" if val > 0 else "red" if val < 0 else "black"
            return f'<span style="color:{color}">{val:.4f}</span>'

        # Apply HTML formatting to sentiment column
        df_display = df.copy()
        df_display["Sentiment Score"] = df_display["Sentiment Score"].apply(lambda x: color_sentiment(x))

        # Display with HTML
        st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown("---")
    st.header("News Articles")

    # Display news for each topic
    for feed in universe_feeds:
        if not feed["articles"]:
            continue

        st.subheader(f"{feed['topic'].upper()} ({feed['article_count']} articles)")

        # Display each news article
        for item in feed["articles"]:
            col1, col2 = st.columns([1, 3])

            with col1:
                st.markdown(f"<h3 style='text-align:left;'>{feed['topic'].upper()}</h3>", unsafe_allow_html=True)

                sentiment_score = item["sentiment"]
                if sentiment_score > 0:
                    st.markdown(
                        f"<h3 style='color:green'><b>Sentiment:</b> {sentiment_score:.4f}</h3>",
                        unsafe_allow_html=True,
                    )
                elif sentiment_score < 0:
                    st.markdown(
                        f"<h3 style='color:red'><b>Sentiment:</b> {sentiment_score:.4f}</h3>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(f"<h3><b>Sentiment:</b> {sentiment_score:.4f}</h3>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"### {item['headline']}")
                st.caption(f"Published: {item['published_date']}")
                st.write(item["description"][:200] + ("..." if len(item["description"]) > 200 else ""))

            st.divider()
