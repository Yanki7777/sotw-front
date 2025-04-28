"""UI component for displaying Alpha Vantage news sentiment."""

import streamlit as st
import pandas as pd
from feeds.alpha_feed import process_alpha_feed

def display_alpha_source(universe):
   
    if not universe:
        st.warning("No universe selected.")
        return

    # Pass the universe directly
    with st.spinner(f"Fetching news for {len(universe.get('topics'))} topic(s)..."):
        all_topic_news, topic_averages, overall_sentiment_average, latest_articles, article_counts = process_alpha_feed(universe)

    print(f"ALPHA source data summary: {len(all_topic_news)} data points analyzed across {len(topic_averages)} topics")

    if not any(all_topic_news.values()):
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

    # Create a dataframe to display individual topic sentiments with article counts and latest article dates
    topic_data = []
    for topic, avg in topic_averages.items():
        latest_date = ""
        if topic in latest_articles and latest_articles[topic] and "published_on" in latest_articles[topic]:
            latest_date = latest_articles[topic]["published_on"]

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
        st.subheader("Alpha topic Sentiment Scores")

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

                st.image(item["banner_image"], width=150)

                # Display sentiment with appropriate color based on score
                sentiment = item["sentiment"]
                sentiment_score = item["sentiment_score"]

                if sentiment_score > 0:
                    st.markdown(
                        f"<h3 style='color:green'><b>Sentiment:</b> {sentiment} ({sentiment_score:.2f})</h3>",
                        unsafe_allow_html=True,
                    )
                elif sentiment_score < 0:
                    st.markdown(
                        f"<h3 style='color:red'><b>Sentiment:</b> {sentiment} ({sentiment_score:.2f})</h3>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"<h3><b>Sentiment:</b> {sentiment} ({sentiment_score:.2f})</h3>", unsafe_allow_html=True
                    )

                # Display relevance score
                if "relevance_score" in item:
                    relevance_score = item["relevance_score"]
                    st.markdown(f"<h4><b>Relevance:</b> {relevance_score:.2f}</h4>", unsafe_allow_html=True)

            with col2:
                st.markdown(f"### [{item['title']}]({item['url']})")
                st.caption(f"Source: {item['source']} | Published: {item['published_on']}")
                st.write(item["summary"][:200] + ("..." if len(item["summary"]) > 200 else ""))

            st.divider()
