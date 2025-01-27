import streamlit as st
import pandas as pd
from datetime import datetime
import time
from scraper import WebScraper
from change_detector import ChangeDetector
from notifier import EmailNotifier
from data_manager import DataManager
from apscheduler.schedulers.background import BackgroundScheduler
from diff_visualizer import DiffVisualizer

# Initialize components
data_manager = DataManager()
scraper = WebScraper()
change_detector = ChangeDetector()
notifier = EmailNotifier()
diff_visualizer = DiffVisualizer()

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def check_website(url: str):
    """Perform website check and detect changes"""
    try:
        with st.spinner(f"Checking {url}..."):
            current_content = scraper.scrape_website(url)
            changes = change_detector.detect_changes(current_content)

            if changes:
                data_manager.store_changes(changes, url)
                notifier.send_notification(changes)
                st.success(f"Found {len(changes)} changes on {url}")

                # Display the changes immediately
                with st.expander(f"Latest Changes for {url}", expanded=True):
                    for change in changes:
                        st.write(f"Detected on {change['timestamp']}")
                        st.write("Type:", change['type'])
                        st.write("Location:", change['location'])

                        # Calculate and display change statistics
                        stats = diff_visualizer.get_diff_stats(change['before'], change['after'])
                        st.write("Change Statistics:")
                        stat_cols = st.columns(3)
                        with stat_cols[0]:
                            st.metric("Words Added", stats['words_added'])
                        with stat_cols[1]:
                            st.metric("Words Removed", stats['words_removed'])
                        with stat_cols[2]:
                            st.metric("Total Changes", stats['total_changes'])

                        # Advanced diff visualization
                        diff_visualizer.visualize_diff(change['before'], change['after'])
                        st.divider()
            else:
                st.info(f"No changes detected on {url}")

    except Exception as e:
        st.error(f"Error checking website: {str(e)}")

# Streamlit UI
st.title("Website Monitoring Tool")
st.subheader("Monitor Multiple Websites for Changes")

# Website Management
with st.sidebar:
    st.header("Website Management")

    # Add new website
    with st.form("add_website"):
        new_url = st.text_input("Website URL")
        check_frequency = st.selectbox(
            "Check frequency",
            ["1 hour", "6 hours", "12 hours", "24 hours"],
            key="check_frequency"
        )

        if st.form_submit_button("Add Website"):
            if new_url:
                website_config = {
                    "url": new_url,
                    "frequency": check_frequency,
                    "added_at": datetime.now().isoformat()
                }
                data_manager.store_website_config(website_config)

                # Add to scheduler
                freq_map = {
                    "1 hour": 3600,
                    "6 hours": 21600,
                    "12 hours": 43200,
                    "24 hours": 86400
                }

                scheduler.add_job(
                    check_website,
                    'interval',
                    seconds=freq_map[check_frequency],
                    id=f'check_{new_url}',
                    args=[new_url]
                )
                st.success(f"Added {new_url} to monitoring")

    # Email configuration
    st.header("Notifications")
    email = st.text_input("Notification email", key="email")
    if st.button("Save Email"):
        notifier.set_email(email)
        st.success("Email saved!")

    # Manage existing websites
    st.header("Monitored Websites")
    websites = data_manager.get_website_configs()
    for website in websites:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(website['url'])
        with col2:
            if st.button("Remove", key=f"remove_{website['url']}"):
                scheduler.remove_job(f"check_{website['url']}")
                data_manager.delete_website_config(website['url'])
                st.rerun()

# Display changes
st.header("Recent Changes")
changes = data_manager.get_recent_changes()

if not changes:
    st.info("No changes detected yet")
else:
    # Group changes by website
    website_changes = {}
    for change in changes:
        url = change['url']
        if url not in website_changes:
            website_changes[url] = []
        website_changes[url].append(change)

    # Display changes by website
    for url, site_changes in website_changes.items():
        with st.expander(f"Changes for {url}"):
            for change in site_changes:
                # Change metadata
                st.write(f"Detected on {change['timestamp']}")
                st.write("Type:", change['type'])
                st.write("Location:", change['location'])

                # Calculate and display change statistics
                stats = diff_visualizer.get_diff_stats(change['before'], change['after'])
                st.write("Change Statistics:")
                stat_cols = st.columns(3)
                with stat_cols[0]:
                    st.metric("Words Added", stats['words_added'])
                with stat_cols[1]:
                    st.metric("Words Removed", stats['words_removed'])
                with stat_cols[2]:
                    st.metric("Total Changes", stats['total_changes'])

                # Advanced diff visualization
                diff_visualizer.visualize_diff(change['before'], change['after'])
                st.divider()

# Manual check button
if websites:
    if st.button("Check All Now"):
        st.write("Starting website checks...")
        for website in websites:
            check_website(website['url'])
        st.success("All checks completed!")

# Show monitoring status
st.sidebar.header("Monitoring Status")
for job in scheduler.get_jobs():
    st.sidebar.write(f"Next check for {job.args[0]}: {job.next_run_time}")


# Demo section
st.header("Visualization Demo")
st.write("Here's an example of how changes are visualized when detected:")

# Sample change for demonstration
demo_before = """Welcome to our Website
We offer high-quality products.
Contact us at contact@example.com
Visit our store at 123 Main Street."""

demo_after = """Welcome to our Updated Website
We offer premium high-quality products and services.
Contact us at support@example.com
Visit our new store at 456 Market Street.
Follow us on social media!"""

# Show demo visualization
with st.expander("Demo Change Visualization", expanded=True):
    st.write("Sample website content change:")

    # Calculate and display change statistics
    demo_stats = diff_visualizer.get_diff_stats(demo_before, demo_after)
    st.write("Change Statistics:")
    demo_cols = st.columns(3)
    with demo_cols[0]:
        st.metric("Words Added", demo_stats['words_added'])
    with demo_cols[1]:
        st.metric("Words Removed", demo_stats['words_removed'])
    with demo_cols[2]:
        st.metric("Total Changes", demo_stats['total_changes'])

    # Show the actual diff visualization
    diff_visualizer.visualize_diff(demo_before, demo_after)