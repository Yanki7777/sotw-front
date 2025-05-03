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

    # Arrange buttons horizontally at the top
    cols = st.columns(len(sources))
    
    # Initialize session state if not already
    if 'active_source' not in st.session_state:
        st.session_state.active_source = None

    # Render buttons
    for idx, (name, _) in enumerate(sources.items()):
        with cols[idx]:
            if st.button(
                f"Fetch {name}",
                use_container_width=True,
                key=f"fetch_{name.lower()}"
            ):
                st.session_state.active_source = name

    st.divider()

    # Display results in full width below buttons
    active = st.session_state.get('active_source')
    if active:
        display_func = sources[active]
        display_func(universe)
