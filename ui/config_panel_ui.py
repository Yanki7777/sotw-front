"""Configuration panel for the Reddit Sentiment Analysis app."""

import streamlit as st
from api_client import APIClient


def configure_sidebar():
    """Configure the sidebar and return user inputs."""
    st.sidebar.title("Configuration")

    # Universe selector
    universes = APIClient.get_all_universes()
    universe_names = [u.get("universe_name") for u in universes]
    selected_universe_name = st.sidebar.selectbox("Select Universe", universe_names)
    # Find the actual universe object
    selected_universe = next((u for u in universes if u.get("universe_name") == selected_universe_name), None)

    # Configure topic mentions counter
    dark_mode = configure_mentions_counter()

    return dark_mode, selected_universe


def configure_mentions_counter():
    """Configure the app settings in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("App Settings")

    # Add dark mode toggle
    dark_mode = st.sidebar.checkbox("Dark Mode", value=False)

    return dark_mode
