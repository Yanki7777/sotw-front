"""topic mentions display module for the Reddit Sentiment Analysis app."""

import streamlit as st
from feeds.reddit_feed import count_topic_mentions_in_subreddit


def display_topic_mentions(
    subreddits, topics, max_posts, positive_karma_only, hours_lookback=24, scan_all_comments=False
):
    """Display counts of topic mentions across subreddits in the last day."""
    st.subheader(f"Reddit topic Mentions (Last {hours_lookback} Hours)")

    # Show analysis scope information
    st.caption(f"Analyzing {len(subreddits)} subreddits for mentions of {len(topics)} topics")

    # Add note about scanning mode
    if scan_all_comments:
        st.info("Scanning all comments in submissions, even if the submission itself doesn't mention the topic.")
    else:
        st.info("Only scanning comments in submissions that mention the topic.")

    with st.spinner("Counting topic mentions..."):
        # Create a progress bar
        progress_bar = st.progress(0)
        total_operations = len(subreddits) * len(topics)
        completed_operations = 0

        # Create a container for results
        mentions_container = st.container()

        # Store results for display
        all_results = {}

        for topic in topics:
            topic_total = {"submission_count": 0, "comment_count": 0, "total_mentions": 0}
            topic_results = []

            for subreddit in subreddits:
                # Call the function that counts mentions
                result = count_topic_mentions_in_subreddit(
                    subreddit,
                    topic,
                    max_submissions=max_posts,
                    positive_karma_only=positive_karma_only,
                    hours_lookback=hours_lookback,
                    scan_all_comments=scan_all_comments,
                )

                topic_results.append(result)

                # Update totals
                topic_total["submission_count"] += result["submission_count"]
                topic_total["comment_count"] += result["comment_count"]
                topic_total["total_mentions"] += result["total_mentions"]

                # Update progress
                completed_operations += 1
                progress_bar.progress(completed_operations / total_operations)

            all_results[topic] = {"by_subreddit": topic_results, "totals": topic_total}

        # Display results in a nice format
        with mentions_container:
            # First display a summary table for all topics
            st.subheader("Summary of All topics")
            summary_data = []
            for topic, data in all_results.items():
                summary_data.append(
                    {
                        "topic": topic.upper(),
                        "Posts": data["totals"]["submission_count"],
                        "Comments": data["totals"]["comment_count"],
                        "Total Mentions": data["totals"]["total_mentions"],
                    }
                )

            st.table(summary_data)

            # Then display detailed information for each topic
            st.subheader("Detailed Breakdown by Subreddit")
            for topic, data in all_results.items():
                with st.expander(f"🔍 {topic.upper()} - {data['totals']['total_mentions']} mentions"):
                    detail_data = []
                    for result in data["by_subreddit"]:
                        detail_data.append(
                            {
                                "Subreddit": f"r/{result['subreddit']}",
                                "Posts": result["submission_count"],
                                "Comments": result["comment_count"],
                                "Total": result["total_mentions"],
                            }
                        )
                    st.table(detail_data)
