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
from bs4 import BeautifulSoup
from timeline_visualizer import TimelineVisualizer

# Initialize components
data_manager = DataManager()
scraper = WebScraper()
change_detector = ChangeDetector()
notifier = EmailNotifier()
diff_visualizer = DiffVisualizer()
timeline_visualizer = TimelineVisualizer()

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
            else:
                st.info(f"No changes detected on {url}")

    except Exception as e:
        st.error(f"Error checking website: {str(e)}")

# Streamlit UI
st.title("Website Monitoring Tool")
st.subheader("Monitor Multiple Websites for Changes")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["Website Management", "Change Timeline", "Demo"])

with tab1:
    # Website Management
    col1, col2 = st.columns([2, 1])

    with col1:
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

    with col2:
        # Email configuration
        st.subheader("Notifications")
        email = st.text_input("Notification email", key="email")
        if st.button("Save Email"):
            notifier.set_email(email)
            st.success("Email saved!")

    # Manage existing websites
    st.subheader("Monitored Websites")
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

with tab2:
    # Display changes with timeline
    st.header("Website Changes Timeline")
    changes = data_manager.get_recent_changes()

    if not changes:
        st.info("No changes detected yet. Changes will appear here once detected.")
    else:
        # Display interactive timeline
        timeline_visualizer.visualize_timeline(changes)

    # Manual check button
    if websites:
        if st.button("Check All Now"):
            st.write("Starting website checks...")
            for website in websites:
                check_website(website['url'])
            st.success("All checks completed!")

    # Show monitoring status
    st.subheader("Monitoring Status")
    for job in scheduler.get_jobs():
        st.write(f"Next check for {job.args[0]}: {job.next_run_time}")

with tab3:
    # Demo section
    st.header("Change Visualization Demo")
    st.write("Here's an example of how changes are visualized when detected:")

    # Sample changes for demonstration
    demo_before_html = """
    <nav class="main-menu">
        <a href="/" style="font-family: Arial; font-size: 16px;">Home</a>
        <a href="/products" style="font-family: Arial; font-size: 16px;">Products</a>
        <a href="/contact" style="font-family: Arial; font-size: 16px;">Contact</a>
    </nav>
    <div class="content" style="font-family: Arial; color: #333;">
        <h1 style="font-size: 24px;">Welcome to our Website</h1>
        <p style="font-size: 16px;">We offer high-quality products.</p>
        <p>Contact us at contact@example.com</p>
        <p>Visit our store at 123 Main Street.</p>
    </div>
    """

    demo_after_html = """
    <nav class="main-menu">
        <a href="/" style="font-family: Helvetica; font-size: 18px;">Home</a>
        <a href="/products" style="font-family: Helvetica; font-size: 18px;">Products</a>
        <a href="/about" style="font-family: Helvetica; font-size: 18px;">About Us</a>
        <a href="/contact" style="font-family: Helvetica; font-size: 18px;">Contact</a>
    </nav>
    <div class="content" style="font-family: Helvetica; color: #444;">
        <h1 style="font-size: 28px;">Welcome to our Updated Website</h1>
        <p style="font-size: 18px;">We offer premium high-quality products and services.</p>
        <p>Contact us at support@example.com</p>
        <p>Visit our new store at 456 Market Street.</p>
        <p>Follow us on social media!</p>
    </div>
    """

    # Show demo visualization
    with st.expander("Demo Change Visualization", expanded=True):
        # Create BeautifulSoup objects to parse HTML
        soup_before = BeautifulSoup(demo_before_html, 'html.parser')
        soup_after = BeautifulSoup(demo_after_html, 'html.parser')

        timestamp = datetime.now().isoformat()

        # Extract components for comparison
        before_data = {
            'text_content': soup_before.get_text(),
            'timestamp': timestamp,
            'styles': scraper._extract_styles(soup_before),
            'menu_structure': scraper._extract_menu_structure(soup_before)
        }

        after_data = {
            'text_content': soup_after.get_text(),
            'timestamp': timestamp,
            'styles': scraper._extract_styles(soup_after),
            'menu_structure': scraper._extract_menu_structure(soup_after)
        }

        # Show text changes
        st.write("### Text Content Changes")
        diff_visualizer.visualize_diff(before_data['text_content'], after_data['text_content'])

        # Show style changes
        st.write("### Style Changes")
        style_changes = change_detector._compare_styles(
            before_data['styles'],
            after_data['styles'],
            timestamp
        )

        for change in style_changes:
            st.write(f"**{change['type'].replace('_', ' ').title()}**")
            if change['before']:
                st.write("Removed:", change['before'])
            if change['after']:
                st.write("Added:", change['after'])
            st.divider()

        # Show menu changes
        st.write("### Menu Structure Changes")
        menu_changes = change_detector._compare_menu_structure(
            before_data['menu_structure'],
            after_data['menu_structure'],
            timestamp
        )

        for change in menu_changes:
            st.write("**Navigation Menu Changes:**")
            st.write("Before:")
            st.code(change['before'])
            st.write("After:")
            st.code(change['after'])