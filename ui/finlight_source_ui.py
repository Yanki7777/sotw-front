"""UI component for displaying Finlight news sentiment."""

import streamlit as st
import pandas as pd
from api_client import APIClient


def display_finlight_source(universe):
    if not universe:
        st.warning("No universe selected.")
        return

    # Pass the universe directly
    with st.spinner(f"Fetching news for {len(universe.get('topics'))} topic(s)..."):
        all_topic_news, topic_averages, overall_sentiment_average, latest_articles, article_counts = (
            APIClient.process_finlight_feed(universe)
        )

    print(
        f"FINLIGHT source data summary: {len(all_topic_news)} data points analyzed across {len(topic_averages)} topics"
    )

    if not any(all_topic_news.values()):
        st.warning("No news data found for the selected topics.")
        return

    # Display overall sentiment average
    st.header("Finlight Sentiment Analysis")

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

    # Create a dataframe to display individual topic sentiments with article counts and latest article dates
    topic_data = []
    for topic, avg in topic_averages.items():
        latest_date = ""
        if topic in latest_articles and latest_articles[topic] and "published_date" in latest_articles[topic]:
            latest_date = latest_articles[topic]["published_date"]

        topic_data.append(
            {
                "topic": topic,
                "Sentiment Score": avg,
                "Articles": article_counts.get(topic, 0),
                "Latest Article": latest_date,
            }
        )

    if topic_data:
        df = pd.DataFrame(topic_data)
        st.subheader("Finlight Topic Sentiment Scores")

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
    for topic, news_items in all_topic_news.items():
        if not news_items:
            continue

        st.subheader(f"{topic.upper()} ({article_counts.get(topic, 0)} articles)")

        # Display each news article
        for item in news_items:
            col1, col2 = st.columns([1, 3])

            with col1:
                # Display topic symbol prominently
                st.markdown(f"<h3 style='text-align:left;'>{topic.upper()}</h3>", unsafe_allow_html=True)

                # Finlight articles may not have images, so skip or use a placeholder
                # st.image(item.get("banner_image", ""), width=150)

                # Display sentiment score only, with color
                sentiment_score = float(item.get("sentiment", 0))

                if sentiment_score > 0:
                    st.markdown(
                        f"<h3 style='color:green'><b>Sentiment Score:</b> {sentiment_score:.2f}</h3>",
                        unsafe_allow_html=True,
                    )
                elif sentiment_score < 0:
                    st.markdown(
                        f"<h3 style='color:red'><b>Sentiment Score:</b> {sentiment_score:.2f}</h3>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(f"<h3><b>Sentiment Score:</b> {sentiment_score:.2f}</h3>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"### {item.get('title', '')}")
                st.caption(f"Published: {item.get('published_date', '')}")
                st.write(item.get("description", "")[:500] + ("..." if len(item.get("description", "")) > 500 else ""))

            st.divider()
