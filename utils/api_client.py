"""API client for interacting with the backend API."""

import requests
import pandas as pd
from typing import Optional
import streamlit as st
from config import API_BASE_URL


class APIClient:
    """Client for interacting with the SOTW API."""

    @staticmethod
    def get_health_status():
        """Check API health status."""
        try:
            response = requests.get(f"{API_BASE_URL}/health")
            return response.json()
        except Exception as e:
            return {"status": "ERROR", "db": f"ERROR: {str(e)}", "message": str(e)}

    @staticmethod
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_all_universes():
        """Get all universes from the API."""
        try:
            response = requests.get(f"{API_BASE_URL}/db/universes")
            return response.json().get("universes", [])
        except Exception as e:
            print(f"Error fetching universes: {e}")
            return []

   
    @staticmethod
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_feed_from_db(
        source: Optional[str] = None,
        topic: Optional[str] = None,
        topic_category: Optional[str] = None,
        feature_name: Optional[str] = None,
        feature_category: Optional[str] = None,
        limit: Optional[int] = None,
        universe_name: Optional[str] = None,
    ):
        """Get feed data from the database with optional filters."""
        try:
            params = {
                "source": source,
                "topic": topic,
                "topic_category": topic_category,
                "feature_name": feature_name,
                "feature_category": feature_category,
                "limit": limit,
                "universe_name": universe_name,
            }
            # Remove None values from params
            params = {k: v for k, v in params.items() if v is not None}

            response = requests.get(f"{API_BASE_URL}/db/feed", params=params)
            data = response.json().get("data", [])

            if data:
                df = pd.DataFrame(data)
                # Convert timestamp columns to datetime using ISO8601 format
                for col in ["created_timestamp", "original_timestamp"]:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], format="ISO8601")
                return df
            return None
        except Exception as e:
            print(f"Error fetching feed data: {e}")
            return None

    @staticmethod
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_latest_feed_timestamp(
        source: Optional[str] = None,
        topic: Optional[str] = None,
        feature_name: Optional[str] = None,
        universe_name: Optional[str] = None,
    ):
        """Get the timestamp of the most recent feed entry."""
        try:
            params = {"source": source, "topic": topic, "feature_name": feature_name, "universe_name": universe_name}
            # Remove None values from params
            params = {k: v for k, v in params.items() if v is not None}

            response = requests.get(f"{API_BASE_URL}/db/feed/latest-timestamp", params=params)
            return response.json().get("latest_timestamp")
        except Exception as e:
            print(f"Error fetching latest timestamp: {e}")
            return None

    @staticmethod
    def create_fmp_feed(universe):
        try:
            response = requests.post(f"{API_BASE_URL}/feed/fmp", json=universe)
            data = response.json()
            return data.get("universe_feeds", [])
        except Exception as e:
            print(f"Error processing FMP feed: {e}")
            return []

    @staticmethod
    def create_alpha_feed(universe):
        try:
            response = requests.post(f"{API_BASE_URL}/feed/alpha", json=universe)
            data = response.json()
            return (
                data.get("universe_feeds", []),
                data.get("overall_sentiment_average", 0.0),
            )
        except Exception as e:
            print(f"Error processing Alpha feed: {e}")
            return [], 0.0

    @staticmethod
    def create_newsapi_feed(universe):
        try:
            response = requests.post(f"{API_BASE_URL}/feed/newsapi", json=universe)
            data = response.json()
            return (
                data.get("universe_feeds", []),
                data.get("overall_sentiment_average", 0.0),
            )
        except Exception as e:
            print(f"Error processing NewsAPI feed: {e}")
            return [], 0.0
        
    @staticmethod
    def create_gnews_feed(universe):
        try:
            response = requests.post(f"{API_BASE_URL}/feed/gnews", json=universe)
            data = response.json()
            return data.get("universe_feeds", []), data.get("overall_sentiment_average", 0)
        except Exception as e:
            print(f"Error processing GNews feed: {e}")
            return [], 0

    @staticmethod
    def create_finlight_feed(universe):
        try:
            response = requests.post(f"{API_BASE_URL}/feed/finlight", json=universe)
            data = response.json()
            return data.get("universe_feeds", []), data.get("overall_sentiment_average", 0)
        except Exception as e:
            print(f"Error processing Finlight feed: {e}")
            return [], 0

    @staticmethod
    def create_reddit_feed(universe):
        try:
            response = requests.post(f"{API_BASE_URL}/feed/reddit", json=universe)
            data = response.json()
            return data.get("universe_feeds", []), data.get("overall_sentiment_average", 0)
        except Exception as e:
            print(f"Error processing Reddit feed: {e}")
            return [], 0

    @staticmethod
    def create_meteo_feed(universe):
        try:
            response = requests.post(f"{API_BASE_URL}/feed/meteo", json=universe)
            data = response.json()
            return data.get("universe_feeds", [])
        except Exception as e:
            print(f"Error processing Meteo feed: {e}")
            return []

    @staticmethod
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_top_news(max_results=10):
        """Get top news articles."""
        try:
            response = requests.get(f"{API_BASE_URL}/news/top", params={"max_results": max_results})
            data = response.json()
            return data.get("data", []), data.get("count", 0)
        except Exception as e:
            print(f"Error fetching top news: {e}")
            return [], 0
