"""Central configuration for SOTW frontend"""
from dotenv import load_dotenv
import os

load_dotenv()

# Set API_ENV to 'development' or 'production' in your environment or .env file
API_ENV = os.environ.get("API_ENV", "development")
API_BASE_URLS = {
    "development": "http://localhost:8000",
    "production": "https://api.stateoftheworld.com",  # Replace with your actual production API URL
}
API_BASE_URL = API_BASE_URLS.get(API_ENV, API_BASE_URLS["development"])


APP_TITLE = "📈 State Of The World"
APP_ICON = "📈"

STREAMLIT_AUTOREFRESH_INTERVAL = 120  # Auto-refresh interval in seconds for the Streamlit UI

# Sentiment thresholds and colors
NEGATIVE_SENTIMENT_THRESHOLD = -0.35
POSITIVE_SENTIMENT_THRESHOLD = 0.35
SENTIMENT_COLORS = {"negative": "red", "neutral": "gray", "positive": "blue"}

