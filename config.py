"""Central configuration for SOTW frontend """

import os
from dotenv import load_dotenv

load_dotenv()


UNIVERSES_FILE = "../data/universes.json"  # JSON file for storing universes data

APP_TITLE = "📈 State Of The World"
APP_ICON = "📈"

STREAMLIT_AUTOREFRESH_INTERVAL = 120  # Auto-refresh interval in seconds for the Streamlit UI

# Sentiment thresholds and colors
NEGATIVE_SENTIMENT_THRESHOLD = -0.35
POSITIVE_SENTIMENT_THRESHOLD = 0.35
SENTIMENT_COLORS = {"negative": "red", "neutral": "gray", "positive": "blue"}

# Alpha Vantage configuration
ALPHA_RELEVANCE_SCORE = 0.1  # Minimum relevance score threshold for news items
ALPHA_MAX_NEWS = 50  # Maximum number of news items to return
NEWSAPI_MAX_NEWS = 0  # Maximum number of news items to return from NewsAPI
FINLIGHT_MAX_NEWS = 20  # Maximum number of news items to return from Finlight API
GNEWS_MAX_NEWS = 12  # Maximum number of news items to return from Finlight API

# Reddit FEED configuration
REDDIT_MAX_POSTS = 25
REDDIT_POSITIVE_KARMA_ONLY = True  # Default to only include positive karma posts/comments
REDDIT_ALWAYS_COMMENTS = True  # Default to always include comments (even if topic not in submission)


# Database configuration for feeder / backend
DB_USER = "postgres"
DB_PASS = os.getenv("POSTGRES_DB_PASS")
DB_HOST = "sotw.camtqtq63luk.eu-central-1.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "postgres"
