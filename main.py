import streamlit as st
import pandas as pd
from datetime import datetime
import time
from scraper import WebScraper
from change_detector import ChangeDetector
from notifier import EmailNotifier
from data_manager import DataManager
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize components
data_manager = DataManager()
scraper = WebScraper()
change_detector = ChangeDetector()
notifier = EmailNotifier()

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

def check_website():
    """Perform website check and detect changes"""
    try:
        current_content = scraper.scrape_website("https://edicanaturals.com")
        changes = change_detector.detect_changes(current_content)
        
        if changes:
            data_manager.store_changes(changes)
            notifier.send_notification(changes)
            
    except Exception as e:
        st.error(f"Error checking website: {str(e)}")

# Streamlit UI
st.title("Website Monitoring Tool")
st.subheader("Monitor changes on edicanaturals.com")

# Monitoring configuration
with st.sidebar:
    st.header("Configuration")
    frequency = st.selectbox(
        "Check frequency",
        ["1 hour", "6 hours", "12 hours", "24 hours"],
        key="check_frequency"
    )
    
    email = st.text_input("Notification email", key="email")
    
    if st.button("Save Configuration"):
        # Convert frequency to seconds
        freq_map = {
            "1 hour": 3600,
            "6 hours": 21600,
            "12 hours": 43200,
            "24 hours": 86400
        }
        
        # Update scheduler
        scheduler.remove_all_jobs()
        scheduler.add_job(
            check_website,
            'interval',
            seconds=freq_map[frequency],
            id='website_check'
        )
        
        notifier.set_email(email)
        st.success("Configuration saved!")

# Display changes
st.header("Recent Changes")
changes = data_manager.get_recent_changes()

if not changes:
    st.info("No changes detected yet")
else:
    for change in changes:
        with st.expander(f"Change detected on {change['timestamp']}"):
            st.write("Type:", change['type'])
            st.write("Location:", change['location'])
            
            # Display diff
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Before")
                st.text(change['before'])
            with col2:
                st.subheader("After")
                st.text(change['after'])

# Manual check button
if st.button("Check Now"):
    with st.spinner("Checking website..."):
        check_website()
    st.success("Check completed!")

# Show monitoring status
st.sidebar.header("Monitoring Status")
next_run = scheduler.get_jobs()[0].next_run_time if scheduler.get_jobs() else None
st.sidebar.write(f"Next check: {next_run}")
