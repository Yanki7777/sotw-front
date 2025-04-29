"""Streamlit UI for the Reddit Sentiment Analysis app."""
# Add feeder path from backend
import sys
from pathlib import Path

# Append the parent directory (../sotw-backend) to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "sotw-feeder"))

from datetime import datetime

# Import UI components
from ui.config_panel_ui import configure_mentions_counter, configure_sidebar
from ui.reddit_source_ui import display_reddit_source
from ui.alpha_source_ui import display_alpha_source
from ui.universe_ui import display_universe
from ui.newsapi_source_ui import display_newsapi_source
from ui.topics_ui import display_topic
from ui.finlight_source_ui import display_finlight_source
from ui.gnews_source_ui import display_gnews_source
from ui.meteo_source_ui import display_meteo_source

# Import configuration
from config import APP_TITLE, APP_ICON

# Apply patches before importing streamlit
from streamlit_patches import apply_torch_classes_patch

apply_torch_classes_patch()
import streamlit as st

# Import API client to store universes in session state
from api_client import APIClient


def streamlit_main():
    """Set up and run the Streamlit UI."""
    # Configure page first
    st.set_page_config(
        page_title=APP_TITLE.replace("📊", "").strip(),
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current time
    print(f"{current_time} ------------------------------ Streamlit UI -------------------------------")

    # Initialize universes in session state
    if "universes" not in st.session_state:
        st.session_state.universes = APIClient.get_all_universes()

    st.title(APP_TITLE)

    # Add Karma button immediately after the app title
    karma_button = st.button("Karma", use_container_width=True)
    if karma_button:
        pass  # Add Karma functionality here if needed

    # Configure sidebar component (returns dark_mode and selected_universe)
    dark_mode, selected_universe = configure_sidebar()

    # --- Fix: Store and update selected_universe in session_state ---
    if "selected_universe" not in st.session_state:
        st.session_state["selected_universe"] = selected_universe
    # If the sidebar selection changed, update session_state
    if selected_universe != st.session_state["selected_universe"]:
        st.session_state["selected_universe"] = selected_universe
        # --- Refresh universe and topic dashboards when universe changes ---
        st.session_state["refresh_universe_dashboard"] = True
        st.session_state["refresh_topic_dashboard"] = True

    universe = st.session_state["selected_universe"]
    st.markdown(
        f"<div style='text-align:left; font-size:1.5rem; margin-top:1.2em; color:#888;'>Universe: <b>{universe.get('universe_name')}</b></div>",
        unsafe_allow_html=True,
    )

    print(f"---------------- Selected universe: {universe}")
    # ---------------------------------------------------------------

    if dark_mode:
        # Apply dark theme CSS
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

    # Remove "Karma" from main_tabs
    main_tabs = st.tabs(["Universe", "Topic", "Sources"])
    print(f"---------------- Current universe: {universe}")

    with main_tabs[0]:
        display_universe(universe)

    with main_tabs[1]:
        display_topic(universe)

    with main_tabs[2]:
        source_tabs = st.tabs(["REDDIT source", "ALPHA source", "NEWSAPI source", "FINLIGHT source", "GNEWS source", "METEO source"])

        with source_tabs[0]:
            col1, col2 = st.columns([1, 5])
            with col1:
                fetch_reddit_button = st.button("Fetch REDDIT", use_container_width=True)

            if fetch_reddit_button:
                display_reddit_source(universe)

        with source_tabs[1]:
            col1, col2 = st.columns([1, 5])
            with col1:
                fetch_alpha_news_button = st.button("Fetch ALPHA News", use_container_width=True)

            # Handle news sentiment fetching when button is pressed
            if fetch_alpha_news_button:
                display_alpha_source(universe)

        with source_tabs[2]:
            col1, col2 = st.columns([1, 5])
            with col1:
                fetch_newsapi_button = st.button("Fetch NEWSAPI", use_container_width=True)

            # Handle NewsAPI sentiment fetching when button is pressed
            if fetch_newsapi_button:
                display_newsapi_source(universe)

        with source_tabs[3]:
            col1, col2 = st.columns([1, 5])
            with col1:
                fetch_finlight_button = st.button("Fetch FINLIGHT", use_container_width=True)

            if fetch_finlight_button:
                display_finlight_source(universe)
                
        with source_tabs[4]:
            col1, col2 = st.columns([1, 5])
            with col1:
                fetch_gnews_button = st.button("Fetch GNEWS", use_container_width=True)

            if fetch_gnews_button:
                display_gnews_source(universe)
                
        with source_tabs[5]:
            col1, col2 = st.columns([1, 5])
            with col1:
                fetch_meteo_button = st.button("Fetch METEO", use_container_width=True)

            if fetch_meteo_button:
                display_meteo_source(universe)


if __name__ == "__main__":
    streamlit_main()
