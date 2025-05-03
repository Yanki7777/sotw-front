import streamlit as st
import pandas as pd
from utils.api_client import APIClient


def display_finlight_source(universe):
    if not universe:
        st.warning("No universe selected.")
        return

    # Fetch data from API
    with st.spinner(f"Fetching Finlight data for {len(universe.get('topics', []))} topic(s)..."):
        (
            all_topic_news,
            topic_sentiments,
            overall_sentiment_average,
            topic_finlight_sentiments,
            overall_finlight_sentiment_average,
            latest_articles,
            article_counts,
        ) = APIClient.process_finlight_feed(universe)

    print(
        f"FINLIGHT data summary: {len(all_topic_news)} topics, {len(topic_sentiments)} sentiment entries analyzed."
    )

    if not any(all_topic_news.values()):
        st.warning("No news data found for the selected topics.")
        return

    st.header("Finlight Sentiment Analysis")

    # Overall sentiment
    sentiment_color = "green" if overall_sentiment_average > 0 else "red" if overall_sentiment_average < 0 else "black"
    st.markdown(
        f"<h3 style='color:{sentiment_color}'>Overall Sentiment: {overall_sentiment_average:.4f}</h3>",
        unsafe_allow_html=True,
    )

    # Overall Finlight-specific sentiment
    finlight_color = (
        "green" if overall_finlight_sentiment_average > 0 else "red" if overall_finlight_sentiment_average < 0 else "black"
    )
    st.markdown(
        f"<h4 style='color:{finlight_color}'>Overall Finlight Sentiment: {overall_finlight_sentiment_average:.4f}</h4>",
        unsafe_allow_html=True,
    )

    # Create dataframe for topic sentiments
    topic_data = []
    for topic, avg in topic_sentiments.items():
        finlight_avg = topic_finlight_sentiments.get(topic, 0)
        latest_date = latest_articles.get(topic, {}).get("published_date", "")

        topic_data.append(
            {
                "Topic": topic,
                "Sentiment Score": avg,
                "Finlight Sentiment": finlight_avg,
                "Articles": article_counts.get(topic, 0),
                "Latest Article": latest_date,
            }
        )

    if topic_data:
        df = pd.DataFrame(topic_data)
        st.subheader("Finlight Topic Sentiment Scores")

        # Apply styling to sentiment scores
        def color_sentiment(val):
            color = "green" if val > 0 else "red" if val < 0 else "black"
            return f'<span style="color:{color}">{val:.4f}</span>'

        df_display = df.copy()
        df_display["Sentiment Score"] = df_display["Sentiment Score"].apply(color_sentiment)
        df_display["Finlight Sentiment"] = df_display["Finlight Sentiment"].apply(color_sentiment)

        # Display with HTML
        st.write(
            df_display.to_html(escape=False, index=False),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.header("News Articles")

    # Display articles
    for topic, news_items in all_topic_news.items():
        if not news_items:
            continue

        st.subheader(f"{topic.upper()} ({article_counts.get(topic, 0)} articles)")

        for item in news_items:
            col1, col2 = st.columns([1, 3])

            sentiment_score = float(item.get("sentiment", 0))
            finlight_sentiment = float(item.get("finlight_sentiment", 0))
            sentiment_color = "green" if sentiment_score > 0 else "red" if sentiment_score < 0 else "black"

            with col1:
                st.markdown(f"<h3>{topic.upper()}</h3>", unsafe_allow_html=True)
                st.markdown(
                    f"<h4 style='color:{sentiment_color}'><b>Bert: {sentiment_score:.2f}</b></h4>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<h4 style='color:{sentiment_color}'><b>finlight: {finlight_sentiment:.2f}</b></h4>",
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown(f"### {item.get('title', '')}")
                st.caption(f"Published: {item.get('published_date', '')}")
                content = item.get("content", "")[:600]
                st.write(content + ("..." if len(content) == 600 else ""))

            st.divider()
