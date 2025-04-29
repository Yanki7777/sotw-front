"""Configuration panel for the Reddit Sentiment Analysis app."""

import streamlit as st
from api_client import APIClient
from config import API_BASE_URL
# from datetime import datetime


def configure_sidebar():
    """Configure the sidebar and return user inputs."""

    print(f"API_BASE_URL: {API_BASE_URL}")

    st.sidebar.text(f"Server URL: {API_BASE_URL}")

    # Universe selector
    universes = APIClient.get_all_universes()
    universe_names = [u.get("universe_name") for u in universes]
    selected_universe_name = st.sidebar.selectbox("Select Universe", universe_names)
    # Find the actual universe object
    selected_universe = next((u for u in universes if u.get("universe_name") == selected_universe_name), None)

    # Add top news section to the sidebar first
    display_top_news_sidebar()

    # Now configure app settings (moved below news)
    dark_mode = configure_settings()

    return dark_mode, selected_universe


def configure_settings():
    """Configure the app settings in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("App Settings")

    # Add dark mode toggle
    dark_mode = st.sidebar.checkbox("Dark Mode", value=False)

    return dark_mode


def display_top_news_sidebar():
    """Display top news in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Latest News")

    # Refresh button for news
    refresh_news = st.sidebar.button("Refresh News", use_container_width=True)

    # Initialize news fetching state if not already set
    if "top_news" not in st.session_state or refresh_news:
        # Fix: Use st.spinner() instead of st.sidebar.spinner()
        spinner_placeholder = st.sidebar.empty()
        spinner_placeholder.text("Loading news...")
        try:
            news_articles, count = APIClient.get_top_news(max_results=5)
            st.session_state.top_news = news_articles
            st.session_state.top_news_count = count
        finally:
            spinner_placeholder.empty()

    # Display the news in a single container
    news_container = st.sidebar.container()

    with news_container:
        if st.session_state.top_news:
            for i, article in enumerate(st.session_state.top_news):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                published_date = article.get("published date UTC", "")
                url = article.get("url", "")
                publisher_data = article.get("publisher", "")
                
                # Extract publisher title if publisher is a dictionary
                publisher = publisher_data.get("title", publisher_data) if isinstance(publisher_data, dict) else publisher_data

                # Display each news article with styling
                st.markdown(f"**{title}**")
                st.write(description)

                # Display published date, publisher, and URL in a single line if available
                footer_elements = []
                if published_date:
                    footer_elements.append(f"Published: {published_date}")
                if publisher:
                    footer_elements.append(f"{publisher}")
                if url:
                    footer_elements.append(f"[Read more]({url})")

                if footer_elements:
                    st.caption(" | ".join(footer_elements))

                # Add separator between articles except after the last one
                if i < len(st.session_state.top_news) - 1:
                    st.markdown("---")
        else:
            st.info("No news available at the moment.")
