"""Central configuration for SOTW frontend"""
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Set API_ENV to 'development' or 'production' in your environment or .env file
envi = os.environ.get("ENVIRON").lower()
print(f"Environment: {envi}")
API_BASE_URLS = {
    "development": "http://localhost:8022",
    "production": "http://51.17.12.158:8022",  # AWS EC2 instance
}
API_BASE_URL = API_BASE_URLS.get(envi, API_BASE_URLS["development"])


APP_TITLE = "📈 State Of The World"
APP_ICON = "📈"

STREAMLIT_AUTOREFRESH_INTERVAL = 120  # Auto-refresh interval in seconds for the Streamlit UI

# Sentiment thresholds and colors
NEGATIVE_SENTIMENT_THRESHOLD = -0.35
POSITIVE_SENTIMENT_THRESHOLD = 0.35
SENTIMENT_COLORS = {"negative": "red", "neutral": "gray", "positive": "blue"}
