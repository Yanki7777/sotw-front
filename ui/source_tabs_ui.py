# ui/source_tabs_ui.py

import streamlit as st
from ui.reddit_source_ui import display_reddit_source
from ui.alpha_source_ui import display_alpha_source
from ui.newsapi_source_ui import display_newsapi_source
from ui.gnews_source_ui import display_gnews_source
from ui.finlight_source_ui import display_finlight_source
from ui.meteo_source_ui import display_meteo_source

def display_source_tabs(universe):
    source_tabs = st.tabs(
        ["REDDIT source", "ALPHA source", "NEWSAPI source", "FINLIGHT source", "GNEWS source", "METEO source"]
    )

    sources = [
        (0, "REDDIT", display_reddit_source),
        (1, "ALPHA News", display_alpha_source),
        (2, "NEWSAPI", display_newsapi_source),
        (3, "FINLIGHT", display_finlight_source),
        (4, "GNEWS", display_gnews_source),
        (5, "METEO", display_meteo_source),
    ]

    for idx, name, display_func in sources:
        with source_tabs[idx]:
            col1, col2 = st.columns([1, 5])
            with col1:
                fetch_button = st.button(f"Fetch {name}", use_container_width=True, key=f"fetch_{name.lower()}")
            if fetch_button:
                display_func(universe)
