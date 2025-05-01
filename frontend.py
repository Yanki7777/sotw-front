"""Optimized SOTW Streamlit UI"""

import streamlit as st
from datetime import datetime

from api_client import APIClient
from config import APP_TITLE, APP_ICON
from ui.config_panel_ui import configure_sidebar
from ui.correlation_finder_ui import display_correlation_finder
from ui.source_tabs_ui import display_source_tabs
from ui.universe_ui import display_universe
from ui.topics_ui import display_topic

# Apply patches before importing streamlit
from streamlit_patches import apply_torch_classes_patch

apply_torch_classes_patch()


def initialize_session_state():
    defaults = {
        "top_news": None,
        "universes": APIClient.get_all_universes(),
        "selected_universe": None,
        "show_correlation_finder": False,
        "active_main_tab": 0,
        "refresh_universe_dashboard": False,
        "refresh_topic_dashboard": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

    if st.session_state["top_news"] is None:
        news, count = APIClient.get_top_news(max_results=8)
        st.session_state["top_news"], st.session_state["top_news_count"] = news, count


def setup_page():
    st.set_page_config(
        page_title=APP_TITLE.replace("📊", "").strip(),
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_theme(dark_mode):
    if dark_mode:
        st.markdown(
            """
            <style>
                .stApp {background-color: #1E1E1E; color: #FFFFFF;}
            </style>
            """,
            unsafe_allow_html=True,
        )


def display_header(universe_name):
    st.title(APP_TITLE)
    st.button("Karma", use_container_width=True)

    if st.button("Correlation Finder", use_container_width=True):
        st.session_state.show_correlation_finder = not st.session_state.show_correlation_finder

    st.markdown(
        f"<div style='font-size:1.5rem; margin-top:1.2em; color:#888;'>"
        f"Universe: <b>{universe_name}</b></div>",
        unsafe_allow_html=True,
    )


def main():

    setup_page()
    initialize_session_state()

    dark_mode, selected_universe = configure_sidebar()

    if selected_universe != st.session_state.selected_universe:
        st.session_state.update({
            "selected_universe": selected_universe,
            "refresh_universe_dashboard": True,
            "refresh_topic_dashboard": True,
        })

    apply_theme(dark_mode)

    universe_name = selected_universe.get("universe_name", "Unknown")
    display_header(universe_name)

    if st.session_state.show_correlation_finder:
        display_correlation_finder()
        if st.button("Close Correlation Finder", use_container_width=True):
            st.session_state.show_correlation_finder = False
            st.rerun()

    main_tabs = st.tabs(["Universe", "Topic", "Sources"])

    with main_tabs[0]:
        display_universe(selected_universe)

    with main_tabs[1]:  
        display_topic(selected_universe)

    with main_tabs[2]:
        display_source_tabs(selected_universe)

    tab_query = st.query_params.get("tab", [0])[0]
    try:
        tab_idx = int(tab_query)
        if 0 <= tab_idx < 3:
            st.session_state.active_main_tab = tab_idx
    except ValueError:
        pass


if __name__ == "__main__":
    main()
