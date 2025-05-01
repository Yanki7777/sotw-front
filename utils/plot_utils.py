import plotly.express as px
import numpy as np
import pandas as pd
from utils.api_client import APIClient
from utils.time_utils import (
    TIME_WINDOW_ALL,    
    filter_dataframe_by_time,
)

from config import NEGATIVE_SENTIMENT_THRESHOLD, POSITIVE_SENTIMENT_THRESHOLD, SENTIMENT_COLORS


def create_reddit_source_sentiment_plot(sentiment_scores, num_submissions, num_comments):
    """Create an interactive Plotly histogram of overall sentiment scores."""
    total_submissions = sum(num_submissions.values())
    total_comments = sum(num_comments.values())
    total_count = total_submissions + total_comments

    fig = px.histogram(
        x=sentiment_scores,
        nbins=30,
        color_discrete_sequence=["#6739b7"],
        title="Overall Sentiment Analysis of Reddit Posts & Comments",
        labels={"x": "Compound Sentiment Score", "y": "Frequency"},
        opacity=0.8,
    )

    fig.add_annotation(
        text=f"Total: {total_count} ({total_submissions} submissions, {total_comments} comments)",
        xref="paper",
        yref="paper",
        x=0.02,
        y=0.98,
        showarrow=False,
        font=dict(size=12),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="black",
        borderwidth=1,
        borderpad=5,
        align="left",
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0.02)",
        xaxis=dict(gridcolor="rgba(0,0,0,0.1)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0.1)"),
        hovermode="x",
        margin=dict(l=20, r=20, t=60, b=20),
        bargap=0.1,
    )

    return fig


def create_reddit_source_topic_plot(topic_sentiments, num_submissions, num_comments):
    """Create interactive Plotly histograms for each topic's sentiment scores."""
    topic_COLOR = "#1f77b4"
    topic_figs = {}

    for topic, scores in topic_sentiments.items():
        if scores:
            color = topic_COLOR
            submissions = num_submissions[topic]
            comments = num_comments[topic]
            total = submissions + comments
            avg_sentiment = np.mean(scores)

            fig = px.histogram(
                x=scores,
                nbins=20,
                color_discrete_sequence=[color],
                opacity=0.7,
                title=f"Sentiment Analysis for {topic.upper()}",
                labels={"x": "Compound Sentiment Score", "y": "Frequency"},
            )

            fig.update_xaxes(range=[-1, 1])

            if avg_sentiment < NEGATIVE_SENTIMENT_THRESHOLD:
                avg_color = SENTIMENT_COLORS["negative"]
            elif avg_sentiment > POSITIVE_SENTIMENT_THRESHOLD:
                avg_color = SENTIMENT_COLORS["positive"]
            else:
                avg_color = SENTIMENT_COLORS["neutral"]

            fig.add_annotation(
                text=f"Total: {total} ({submissions} submissions, {comments} comments)<br><b style='color:{avg_color}'>Avg: {avg_sentiment:.3f}</b>",
                xref="paper",
                yref="paper",
                x=0.02,
                y=0.98,
                showarrow=False,
                font=dict(size=12),
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="black",
                borderwidth=1,
                borderpad=5,
                align="left",
            )

            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0.02)",
                xaxis=dict(gridcolor="rgba(0,0,0,0.1)"),
                yaxis=dict(gridcolor="rgba(0,0,0,0.1)"),
                hovermode="x",
                margin=dict(l=20, r=20, t=60, b=20),
                bargap=0.1,
            )

            fig.add_shape(
                type="line",
                x0=avg_sentiment,
                y0=0,
                x1=avg_sentiment,
                y1=1,
                yref="paper",
                line=dict(color="black", width=2, dash="dash"),
            )

            topic_figs[topic] = fig

    return topic_figs


def _create_common_layout(title, axis_labels=None):
    """
    Create a common layout configuration for plots.
    """
    title_font_size = 22
    axis_title_font_size = 16
    tick_font_size = 14
    legend_font_size = 14

    layout = dict(
        hovermode="closest",
        plot_bgcolor="rgba(0,0,0,0.02)",
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            title_font=dict(size=axis_title_font_size),
            tickfont=dict(size=tick_font_size),
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            title_font=dict(size=axis_title_font_size),
            tickfont=dict(size=tick_font_size),
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=500,
        title=dict(font=dict(size=title_font_size), text=title),
        legend=dict(font=dict(size=legend_font_size)),
    )

    if axis_labels and isinstance(axis_labels, dict):
        if "x" in axis_labels:
            layout["xaxis"]["title"] = axis_labels["x"]
        if "y" in axis_labels:
            layout["yaxis"]["title"] = axis_labels["y"]

    return layout


def create_one_feature_plot(universe_name, source, topic, feature_name, time_window=TIME_WINDOW_ALL):
    """
    Create a plot showing feature values over time from the feed data.
    """
    try:
        source = str(source) if source is not None else "unknown"
        feature_name = str(feature_name) if feature_name is not None else "unknown"

        if topic is None:
            df = APIClient.get_feed_from_db(source=source, feature_name=feature_name, universe_name=universe_name)
            topic_display = ""
        else:
            topic = str(topic)
            df = APIClient.get_feed_from_db(
                source=source, topic=topic, feature_name=feature_name, universe_name=universe_name
            )
            topic_display = topic

        if df is None or df.empty:
            print(f"No data available for {topic_display} {feature_name} from {source}")
            return None, None

        df = filter_dataframe_by_time(df, time_window)

        if df.empty:
            print(f"No data available for the selected time window: {time_window}")
            return None, None

        plot_key = f"{source}_{topic_display.replace(' ', '_')}_{feature_name}_{time_window}"

        try:
            df["feature_value"] = pd.to_numeric(df["feature_value"])
            numeric_values = True
        except (ValueError, TypeError):
            numeric_values = False
            print("Feature plot --- Feature values are not numeric and will be treated as categorical")

        if topic_display != "":
            plot_title = f"{topic_display} - {feature_name} from {source}"
        else:
            plot_title = f"{feature_name} from {source}"

        plot_params = {
            "x": "created_timestamp",
            "y": "feature_value",
            "title": plot_title,
            "labels": {"created_timestamp": "Date & Time", "feature_value": feature_name},
            "render_mode": "svg",
        }

        if topic is None:
            plot_params["color"] = "topic"
            plot_params["labels"]["topic"] = "topic"

        if numeric_values:
            plot_params["line_shape"] = "linear"
            fig = px.line(df, **plot_params)
        else:
            fig = px.scatter(df, **plot_params)

        fig.update_layout(_create_common_layout(plot_title, {"x": "Date & Time", "y": feature_name}))

        return fig, plot_key

    except Exception as e:
        print(f"Error creating feature value plot: {e}")
        return None, None
