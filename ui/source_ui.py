import streamlit as st
from ui.reddit_source_ui import display_reddit_source
from ui.alpha_source_ui import display_alpha_source
from ui.newsapi_source_ui import display_newsapi_source
from ui.gnews_source_ui import display_gnews_source
from ui.finlight_source_ui import display_finlight_source
from ui.meteo_source_ui import display_meteo_source

def display_source_fetch_buttons(universe):
    st.header("Data Sources")

    sources = {
        "REDDIT": display_reddit_source,
        "ALPHA News": display_alpha_source,
        "NEWSAPI": display_newsapi_source,
        "FINLIGHT": display_finlight_source,
        "GNEWS": display_gnews_source,
        "METEO": display_meteo_source,
    }

    # Ensure session state initialization
    if 'active_source' not in st.session_state:
        st.session_state.active_source = None

    # Arrange buttons horizontally at the top using columns
    cols = st.columns(len(sources))

    # Render buttons with more explicit logic
    for col, (source_name, display_func) in zip(cols, sources.items()):
        with col:
            if st.button(
                f"Fetch {source_name}",
                use_container_width=True,
                key=f"fetch_{source_name.lower()}"
            ):
                st.session_state.active_source = source_name

    st.divider()

    # Clearly separated results section
    if st.session_state.active_source:
        st.subheader(f"Results from {st.session_state.active_source}")
        sources[st.session_state.active_source](universe)
    else:
        st.info("Please select a data source to fetch results.")
