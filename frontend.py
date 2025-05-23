"""SOTW Streamlit UI"""

import streamlit as st

from utils.api_client import APIClient
from config import APP_TITLE, APP_ICON
from ui.config_panel_ui import configure_sidebar
from ui.correlation_finder_ui import display_correlation_finder
from ui.source_ui import display_source_fetch_buttons
from ui.universe_ui import display_universe
from ui.topics_ui import display_topic
from utils.general_utils import TIME_WINDOW_DAY

# Apply patches before importing streamlit
from streamlit_patches import apply_torch_classes_patch

apply_torch_classes_patch()


def initialize_session_state():
    """
    Initialize Streamlit session state without redundant API calls.
    Checks if data already exists in session state before fetching from API.
    """
    # Set defaults only if the keys are not already in session state
    if "universes" not in st.session_state:
        st.session_state["universes"] = APIClient.get_all_universes()

    if "selected_universe" not in st.session_state:
        st.session_state["selected_universe"] = None

    if "top_news" not in st.session_state or "top_news_count" not in st.session_state:
        news, count = APIClient.get_top_news(max_results=8)
        st.session_state["top_news"] = news
        st.session_state["top_news_count"] = count

    # Set additional default states if needed
    st.session_state.setdefault("show_correlation_finder", False)
    st.session_state.setdefault("active_tab", "universe")
    st.session_state.setdefault("refresh_universe_dashboard", False)
    st.session_state.setdefault("refresh_topic_dashboard", False)    
    st.session_state.setdefault("universe_time_window", TIME_WINDOW_DAY)

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

    # Navigation buttons in a row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "Universe",
            use_container_width=True,
            type="primary" if st.session_state.active_tab == "universe" else "secondary",
        ):
            st.session_state.active_tab = "universe"
            st.session_state.show_correlation_finder = False
            st.rerun()

    with col2:
        if st.button(
            "Topic", use_container_width=True, type="primary" if st.session_state.active_tab == "topic" else "secondary"
        ):
            st.session_state.active_tab = "topic"
            st.session_state.show_correlation_finder = False
            st.rerun()

    with col3:
        if st.button(
            "Sources",
            use_container_width=True,
            type="primary" if st.session_state.active_tab == "sources" else "secondary",
        ):
            st.session_state.active_tab = "sources"
            st.session_state.show_correlation_finder = False
            st.rerun()

    with col4:
        if st.button(
            "Correlation Finder",
            use_container_width=True,
            type="primary" if st.session_state.show_correlation_finder else "secondary",
        ):
            st.session_state.show_correlation_finder = not st.session_state.show_correlation_finder
            if st.session_state.show_correlation_finder:
                st.session_state.active_tab = None
            st.rerun()

    st.markdown(
        f"<div style='font-size:1.5rem; margin-top:1.2em; color:#888;'>Universe: <b>{universe_name}</b></div>",
        unsafe_allow_html=True,
    )


def main():
    setup_page()
    initialize_session_state()

    dark_mode, selected_universe = configure_sidebar()

    if selected_universe != st.session_state.selected_universe:
        st.session_state.update(
            {
                "selected_universe": selected_universe,
                "refresh_universe_dashboard": True,
                "refresh_topic_dashboard": True,
                "active_tab": "universe",  # Force active tab to 'universe'
                "show_correlation_finder": False  # Ensure correlation finder is closed
            }
        )


    apply_theme(dark_mode)

    universe_name = selected_universe.get("universe_name", "Unknown")
    display_header(universe_name)

    # Clear previous content and show only the selected component
    if st.session_state.show_correlation_finder:
        display_correlation_finder()
    elif st.session_state.active_tab == "universe":
        display_universe(selected_universe)
    elif st.session_state.active_tab == "topic":
        display_topic(selected_universe)
    elif st.session_state.active_tab == "sources":
        display_source_fetch_buttons(selected_universe)


    # Handle URL query params for deep linking
    tab_query = st.query_params.get("tab", [None])[0]
    if tab_query:
        tab_mapping = {"0": "universe", "1": "topic", "2": "sources"}
        if tab_query in tab_mapping:
            if st.session_state.active_tab != tab_mapping[tab_query]:
                st.session_state.active_tab = tab_mapping[tab_query]
                st.session_state.show_correlation_finder = False
                st.rerun()


if __name__ == "__main__":
    main()
