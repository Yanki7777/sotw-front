"""Central configuration for SOTW frontend """

APP_TITLE = "📈 State Of The World"
APP_ICON = "📈"

STREAMLIT_AUTOREFRESH_INTERVAL = 120  # Auto-refresh interval in seconds for the Streamlit UI

# Sentiment thresholds and colors
NEGATIVE_SENTIMENT_THRESHOLD = -0.35
POSITIVE_SENTIMENT_THRESHOLD = 0.35
SENTIMENT_COLORS = {"negative": "red", "neutral": "gray", "positive": "blue"}
