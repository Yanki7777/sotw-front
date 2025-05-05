"""UI component for displaying Alpha Vantage news sentiment."""

import streamlit as st
import pandas as pd
from utils.api_client import APIClient


def display_alpha_source(universe):
    if not universe:
        st.warning("No universe selected.")
        return

    # Pass the universe directly
    with st.spinner(f"Fetching news for {len(universe.get('topics'))} topic(s)..."):
        universe_feeds, overall_sentiment_average = APIClient.process_alpha_feed(universe)

    print(f"ALPHA source data summary: {len(universe_feeds)} topics processed")

    if not universe_feeds:
        st.warning("No news data found for the selected topics.")
        return

    # Display overall sentiment average
    st.header("Alpha Sentiment Analysis")

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
    topic_data = [
        {
            "topic": feed["topic"],
            "Sentiment Score": feed["sentiment_average"],
            "Articles": feed["article_count"],
            "Latest Article": feed["latest_article"]["published_on"] if feed["latest_article"] else "",
        }
        for feed in universe_feeds
    ]

    if topic_data:
        df = pd.DataFrame(topic_data)
        st.subheader("Alpha Topic Sentiment Scores")

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

        df["Sentiment Score"] = df["Sentiment Score"].apply(lambda x: color_sentiment(x))

        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown("---")
    st.header("News Articles")

    # Display news for each topic
    for feed in universe_feeds:
        if not feed["articles"]:
            continue

        st.subheader(f"{feed['topic'].upper()} ({feed['article_count']} articles)")

        for item in feed["articles"]:
            col1, col2 = st.columns([1, 3])

            with col1:
                st.markdown(f"<h3 style='text-align:left;'>{feed['topic'].upper()}</h3>", unsafe_allow_html=True)
                st.image(item["banner_image"], width=150)

                sentiment_score = item["sentiment_score"]
                sentiment_color = "green" if sentiment_score > 0 else "red" if sentiment_score < 0 else "black"

                st.markdown(
                    f"<h3 style='color:{sentiment_color}'><b>Sentiment:</b> {item['sentiment']} ({sentiment_score:.2f})</h3>",
                    unsafe_allow_html=True,
                )

                if "relevance_score" in item:
                    st.markdown(f"<h4><b>Relevance:</b> {item['relevance_score']:.2f}</h4>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"### [{item['title']}]({item['url']})")
                st.caption(f"Source: {item['source']} | Published: {item['published_on']}")
                st.write(item["summary"][:200] + ("..." if len(item["summary"]) > 200 else ""))

            st.divider()
