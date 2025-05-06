import streamlit as st
import pandas as pd
from utils.api_client import APIClient


def display_finlight_source(universe):
    if not universe:
        st.warning("No universe selected.")
        return

    # Fetch data from API
    with st.spinner(f"Fetching Finlight data for {len(universe.get('topics', []))} topic(s)..."):
        universe_feeds, overall_average = APIClient.create_finlight_feed(universe)

    print(f"FINLIGHT data summary: {len(universe_feeds)} topics analyzed.")

    if not universe_feeds:
        st.warning("No news data found for the selected topics.")
        return

    st.header("Finlight Source")

    finlight_color = "green" if overall_average > 0 else "red" if overall_average < 0 else "black"
    st.markdown(
        f"<h4 style='color:{finlight_color}'>Overall Finlight Sentiment: {overall_average:.4f}</h4>",
        unsafe_allow_html=True,
    )

    topic_data = []
    for feed in universe_feeds:
        latest_date = feed["latest_article"].get("published_date", "") if feed["latest_article"] else ""

        topic_data.append(
            {
                "Topic": feed["topic"],
                "Finlight Sentiment": feed["finlight_sentiment_average"],
                "FinBERT Sentiment": feed["finbert_sentiment_average"],
                "GPT4.1 Sentiment": feed["gpt41_sentiment_average"],
                "Articles": feed["article_count"],
                "Latest Article": latest_date,
            }
        )

    if topic_data:
        df = pd.DataFrame(topic_data)
        st.subheader("Finlight Topic Sentiment Scores")

        def color_sentiment(val):
            color = "green" if val > 0 else "red" if val < 0 else "black"
            return f'<span style="color:{color}">{val:.4f}</span>'

        df_display = df.copy()
        for sentiment_col in ["Finlight Sentiment", "FinBERT Sentiment", "GPT4.1 Sentiment"]:
            df_display[sentiment_col] = df_display[sentiment_col].apply(color_sentiment)

        st.write(
            df_display.to_html(escape=False, index=False),
            unsafe_allow_html=True,
        )

    st.markdown("---")

    topics_available = [feed["topic"] for feed in universe_feeds]
    selected_topic = st.selectbox("Select Topic to Display Articles", ["All"] + topics_available)

    st.header("News Articles")

    topics_to_display = topics_available if selected_topic == "All" else [selected_topic]

    for feed in universe_feeds:
        if feed["topic"] not in topics_to_display:
            continue

        news_items = feed["articles"]

        if not news_items:
            continue

        st.subheader(f"{feed['topic'].upper()} ({feed['article_count']} articles)")

        for item in news_items:
            col1, col2 = st.columns([1, 3])

            sentiment_score = float(item.get("finlight_sentiment", 0))
            sentiment_color = "green" if sentiment_score > 0 else "red" if sentiment_score < 0 else "black"

            with col1:
                st.markdown(f"<h3>{feed['topic'].upper()}</h3>", unsafe_allow_html=True)
                st.markdown(
                    f"<h4 style='color:{sentiment_color}'><b>Sentiment: {sentiment_score:.2f}</b></h4>",
                    unsafe_allow_html=True,
                )

                images = item.get("images", [])
                if images:
                    img_space1, img_col, img_space2 = st.columns([0.05, 0.9, 0.05])
                    with img_col:
                        st.image(images[0], use_container_width=True)

            with col2:
                st.markdown(f"### {item.get('title', '')}")
                st.caption(f"**Published:** {item.get('published_date', '')}.  **Source:** {item.get('source', '')}")
                st.caption(f"Link: {item.get('link', '')}")
                content = item.get("content", "")[:600]
                st.write(content + ("..." if len(content) == 600 else ""))

            st.divider()
