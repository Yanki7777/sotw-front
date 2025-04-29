"""UI component for displaying Meteo air quality data."""

import streamlit as st
import pandas as pd
from api_client import APIClient


def display_meteo_source(universe):
    if not universe:
        st.warning("No universe selected.")
        return

    # Pass the universe directly
    with st.spinner(f"Fetching air quality data for {len(universe.get('topics'))} location(s)..."):
        topic_air_quality, air_quality_timestamps = APIClient.process_meteo_feed(universe)

    print(f"METEO source data summary: {len(topic_air_quality)} locations analyzed")

    if not topic_air_quality:
        st.warning("No air quality data found for the selected locations.")
        return

    # Display header
    st.header("Meteo Air Quality Analysis")

    # Create a dataframe to display air quality data
    topic_data = []
    for topic, air_quality in topic_air_quality.items():
        if isinstance(air_quality, dict):
            # Extract key metrics
            us_aqi = air_quality.get("us_aqi", "N/A")
            pm10 = air_quality.get("pm10", "N/A")
            pm2_5 = air_quality.get("pm2_5", "N/A")
            carbon_monoxide = air_quality.get("carbon_monoxide", "N/A")
            timestamp = air_quality_timestamps.get(topic, "N/A")

            topic_data.append(
                {
                    "Location": topic,
                    "US AQI": us_aqi,
                    "PM10": pm10,
                    "PM2.5": pm2_5,
                    "CO": carbon_monoxide,
                    "Timestamp": timestamp,
                }
            )
        else:
            # Handle error case
            topic_data.append(
                {
                    "Location": topic,
                    "US AQI": "Error",
                    "PM10": "Error",
                    "PM2.5": "Error",
                    "CO": "Error",
                    "Timestamp": "N/A",
                    "Error": air_quality.get("error", "Unknown error"),
                }
            )

    if topic_data:
        df = pd.DataFrame(topic_data)
        st.subheader("Air Quality Metrics")

        # Use st.write with HTML for custom styling
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

        # Function to color AQI values based on EPA standard
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

        # Apply HTML formatting to AQI column
        df_display = df.copy()
        if "US AQI" in df_display:
            df_display["US AQI"] = df_display["US AQI"].apply(lambda x: color_aqi(x))

        # Display with HTML
        st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown("---")
    st.header("Detailed Air Quality Data")

    # Display detailed data for each location
    for topic, air_quality in topic_air_quality.items():
        if not isinstance(air_quality, dict):
            st.error(f"Error retrieving data for {topic}: {air_quality.get('error', 'Unknown error')}")
            continue

        st.subheader(f"{topic.upper()}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Primary Pollutants")
            metrics = {
                "US AQI": air_quality.get("us_aqi", "N/A"),
                "PM10 (μg/m³)": air_quality.get("pm10", "N/A"),
                "PM2.5 (μg/m³)": air_quality.get("pm2_5", "N/A"),
            }
            for label, value in metrics.items():
                st.metric(label=label, value=value)

        with col2:
            st.markdown("#### Secondary Pollutants")
            metrics = {
                "Carbon Monoxide (μg/m³)": air_quality.get("carbon_monoxide", "N/A"),
                "Nitrogen Dioxide (μg/m³)": air_quality.get("nitrogen_dioxide", "N/A"),
                "Sulphur Dioxide (μg/m³)": air_quality.get("sulphur_dioxide", "N/A"),
                "Ozone (μg/m³)": air_quality.get("ozone", "N/A"),
            }
            for label, value in metrics.items():
                st.metric(label=label, value=value)

        st.caption(f"Data timestamp: {air_quality_timestamps.get(topic, 'N/A')}")
        st.divider()
