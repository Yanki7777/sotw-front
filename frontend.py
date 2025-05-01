"""SOTW Streamlit UI"""

from datetime import datetime

from api_client import APIClient
from ui.config_panel_ui import configure_sidebar
from ui.reddit_source_ui import display_reddit_source
from ui.alpha_source_ui import display_alpha_source
from ui.universe_ui import display_universe
from ui.newsapi_source_ui import display_newsapi_source
from ui.topics_ui import display_topic
from ui.finlight_source_ui import display_finlight_source
from ui.gnews_source_ui import display_gnews_source
from ui.meteo_source_ui import display_meteo_source

from config import APP_TITLE, APP_ICON

# Apply patches before importing streamlit
from streamlit_patches import apply_torch_classes_patch

apply_torch_classes_patch()
import streamlit as st


def streamlit_main():
    """Set up and run the Streamlit UI."""
    # Configure page first
    st.set_page_config(
        page_title=APP_TITLE.replace("📊", "").strip(),
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Preload top news for sidebar if not already in session state
    if "top_news" not in st.session_state:
        news_articles, count = APIClient.get_top_news(max_results=8)
        st.session_state.top_news = news_articles
        st.session_state.top_news_count = count

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current time
    print(f"{current_time} ------------------------------ Streamlit UI -------------------------------")

    # Initialize universes in session state
    if "universes" not in st.session_state:
        st.session_state.universes = APIClient.get_all_universes()

    st.title(APP_TITLE)

    # Track if correlation finder is active
    if "show_correlation_finder" not in st.session_state:
        st.session_state.show_correlation_finder = False

    # Add Karma button immediately after the app title
    karma_button = st.button("Karma", use_container_width=True)
    if karma_button:
        pass  # Add Karma functionality here if needed

    # Add Correlation Finder button below Karma button
    correlation_button = st.button("Correlation Finder", use_container_width=True)
    if correlation_button:
        st.session_state.show_correlation_finder = not st.session_state.show_correlation_finder

    # Display correlation finder if active
    if st.session_state.show_correlation_finder:
        from ui.correlation_finder_ui import display_correlation_finder

        display_correlation_finder()
        # Add a button to close correlation finder
        if st.button("Close Correlation Finder", use_container_width=True):
            st.session_state.show_correlation_finder = False
            st.rerun()

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

    # Keep track of which tab was last selected
    if "active_main_tab" not in st.session_state:
        st.session_state.active_main_tab = 0

    # Create tabs with the active tab selected
    tab_names = ["Universe", "Topic", "Sources"]
    main_tabs = st.tabs(tab_names)

    # Handle each tab separately
    with main_tabs[0]:
        if st.session_state.active_main_tab == 0:
            display_universe(universe)

    with main_tabs[1]:
        if st.session_state.active_main_tab == 1:
            display_topic(universe)

    with main_tabs[2]:
        if st.session_state.active_main_tab == 2:
            source_tabs = st.tabs(
                ["REDDIT source", "ALPHA source", "NEWSAPI source", "FINLIGHT source", "GNEWS source", "METEO source"]
            )

            # Extract the repeated source display pattern into a function
            def display_source_tab(tab_index, source_name, display_function):
                with source_tabs[tab_index]:
                    col1, col2 = st.columns([1, 5])
                    with col1:
                        fetch_button = st.button(f"Fetch {source_name}", use_container_width=True)
                    if fetch_button:
                        display_function(universe)

            # Use the new function for each source tab
            display_source_tab(0, "REDDIT", display_reddit_source)
            display_source_tab(1, "ALPHA News", display_alpha_source)
            display_source_tab(2, "NEWSAPI", display_newsapi_source)
            display_source_tab(3, "FINLIGHT", display_finlight_source)
            display_source_tab(4, "GNEWS", display_gnews_source)
            display_source_tab(5, "METEO", display_meteo_source)

    # Update active tab based on URL hash parameter
    tab_hash = st.query_params.get("tab", [0])[0]
    try:
        tab_index = int(tab_hash)
        if 0 <= tab_index < len(tab_names):
            st.session_state.active_main_tab = tab_index
    except ValueError:
        pass


if __name__ == "__main__":
    streamlit_main()
