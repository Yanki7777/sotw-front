import streamlit as st
import pandas as pd
from utils.api_client import APIClient


def display_meteo_source(universe):
    if not universe:
        st.warning("No universe selected.")
        return

    with st.spinner(f"Fetching air quality data for {len(universe.get('topics'))} location(s)..."):
        universe_feeds = APIClient.process_meteo_feed(universe)

    print(f"METEO source data summary: {len(universe_feeds)} locations analyzed")

    if not universe_feeds:
        st.warning("No air quality data found for the selected locations.")
        return

    st.header("Meteo Air Quality Analysis")

    topic_data = []
    for feed in universe_feeds:
        if "air_quality" in feed:
            aq = feed["air_quality"]
            topic_data.append({
                "Location": feed["city"],
                "US AQI": aq.get("us_aqi", "N/A"),
                "PM10": aq.get("pm10", "N/A"),
                "PM2.5": aq.get("pm2_5", "N/A"),
                "CO": aq.get("carbon_monoxide", "N/A"),
                "Timestamp": feed.get("timestamp", "N/A")
            })
        else:
            topic_data.append({
                "Location": feed["city"],
                "US AQI": "Error",
                "PM10": "Error",
                "PM2.5": "Error",
                "CO": "Error",
                "Timestamp": "N/A",
                "Error": feed.get("error", "Unknown error")
            })

    df = pd.DataFrame(topic_data)
    st.subheader("Air Quality Metrics")

    html = """
    <style>
        table.dataframe {
            font-size: 20px !important;
        }
        table.dataframe td, table.dataframe th {
            text-align: left !important;
            padding: 8px !important;
        }
    </style>
    """
    st.write(html, unsafe_allow_html=True)

    def color_aqi(val):
        try:
            val = float(val)
            if val <= 50:
                return f'<span style="color:green">{val} (Good)</span>'
            elif val <= 100:
                return f'<span style="color:#FFA500">{val} (Moderate)</span>'
            elif val <= 150:
                return f'<span style="color:#FF4500">{val} (Unhealthy for Sensitive Groups)</span>'
            elif val <= 200:
                return f'<span style="color:red">{val} (Unhealthy)</span>'
            elif val <= 300:
                return f'<span style="color:#800080">{val} (Very Unhealthy)</span>'
            else:
                return f'<span style="color:#8B0000">{val} (Hazardous)</span>'
        except (ValueError, TypeError):
            return val

    df_display = df.copy()
    df_display["US AQI"] = df_display["US AQI"].apply(lambda x: color_aqi(x))
    st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown("---")
    st.header("Detailed Air Quality Data")

    for feed in universe_feeds:
        if "air_quality" not in feed:
            st.error(f"Error retrieving data for {feed['city']}: {feed.get('error', 'Unknown error')}")
            continue

        st.subheader(f"{feed['city'].upper()}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Primary Pollutants")
            metrics = {
                "US AQI": feed["air_quality"].get("us_aqi", "N/A"),
                "PM10 (μg/m³)": feed["air_quality"].get("pm10", "N/A"),
                "PM2.5 (μg/m³)": feed["air_quality"].get("pm2_5", "N/A"),
            }
            for label, value in metrics.items():
                st.metric(label=label, value=value)

        with col2:
            st.markdown("#### Secondary Pollutants")
            metrics = {
                "Carbon Monoxide (μg/m³)": feed["air_quality"].get("carbon_monoxide", "N/A"),
                "Nitrogen Dioxide (μg/m³)": feed["air_quality"].get("nitrogen_dioxide", "N/A"),
                "Sulphur Dioxide (μg/m³)": feed["air_quality"].get("sulphur_dioxide", "N/A"),
                "Ozone (μg/m³)": feed["air_quality"].get("ozone", "N/A"),
            }
            for label, value in metrics.items():
                st.metric(label=label, value=value)

        st.caption(f"Data timestamp: {feed.get('timestamp', 'N/A')}")
        st.divider()
