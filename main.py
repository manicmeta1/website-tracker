import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from scraper import WebScraper
from change_detector import ChangeDetector
from notifier import EmailNotifier
from data_manager import DataManager
from apscheduler.schedulers.background import BackgroundScheduler
from diff_visualizer import DiffVisualizer
from bs4 import BeautifulSoup
from timeline_visualizer import TimelineVisualizer

def _normalize_job_id(url: str) -> str:
    """Normalize URL for job ID to ensure consistency"""
    return url.replace('https://', '').replace('http://', '').strip('/')

def check_website(url: str, crawl_all_pages: bool = False):
    """Perform website check and detect changes"""
    try:
        with st.spinner(f"Checking {url}..."):
            current_content = scraper.scrape_website(url, crawl_all_pages)
            changes = change_detector.detect_changes(current_content)

            if changes:
                data_manager.store_changes(changes, url)
                notifier.send_notification(changes)
                st.success(f"Found {len(changes)} changes on {url}")
            else:
                st.info(f"No changes detected on {url}")

    except Exception as e:
        st.error(f"Error checking website: {str(e)}")

# Initialize components
data_manager = DataManager()
scraper = WebScraper()
change_detector = ChangeDetector()
notifier = EmailNotifier()
diff_visualizer = DiffVisualizer(key_prefix="demo")
timeline_visualizer = TimelineVisualizer()

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Streamlit UI
st.set_page_config(layout="wide", page_title="Website Monitor")

# Custom CSS for better visual hierarchy
st.markdown("""
<style>
    .metric-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1rem;
        background-color: white;
    }
    .status-active {
        color: #28a745;
    }
    .status-inactive {
        color: #dc3545;
    }
    .notification-settings {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Create tabs for different sections
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Website Management", "Change Timeline", "Demo"])

with tab1:
    st.title("📊 Monitoring Dashboard")

    # Get all monitored websites and their data
    websites = data_manager.get_website_configs()
    all_changes = data_manager.get_recent_changes()

    if not websites:
        st.info("No websites are being monitored yet. Add websites in the Website Management tab.")
    else:
        # Overview Statistics
        st.subheader("📈 Overview")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Websites Monitored",
                len(websites),
                delta=None,
                help="Total number of websites being monitored"
            )

        with col2:
            active_jobs = len(scheduler.get_jobs())
            st.metric(
                "Active Monitors",
                active_jobs,
                delta=None,
                help="Number of active monitoring jobs"
            )

        with col3:
            recent_changes = len(all_changes)
            st.metric(
                "Recent Changes",
                recent_changes,
                delta=None,
                help="Number of changes detected in the last 24 hours"
            )

        # Individual Website Cards
        st.subheader("🌐 Website Status")

        for website in websites:
            with st.expander(f"📊 {website['url']}", expanded=True):
                cols = st.columns([2, 1])

                with cols[0]:
                    # Website Details
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>Monitoring Details</h4>
                        <p><strong>Check Frequency:</strong> {website['frequency']}</p>
                        <p><strong>Added:</strong> {website['added_at']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Recent Changes
                    website_changes = [c for c in all_changes if c['url'] == website['url']]
                    if website_changes:
                        st.markdown("##### Recent Changes")
                        for change in website_changes[-3:]:  # Show last 3 changes
                            st.markdown(f"""
                            <div style='border-left: 3px solid #1f77b4; padding-left: 10px; margin: 5px 0;'>
                                <p><strong>{change['type'].replace('_', ' ').title()}</strong><br>
                                <small>{change['timestamp']}</small></p>
                            </div>
                            """, unsafe_allow_html=True)

                with cols[1]:
                    # Quick Actions
                    st.markdown("##### Quick Actions")
                    if st.button("Check Now", key=f"quick_check_{website['url']}"):
                        with st.spinner("Checking website..."):
                            check_website(website['url'], website.get('crawl_all_pages', False))

                    # Last check time
                    job = next((job for job in scheduler.get_jobs()
                                  if job.id == f"check_{website['url']}"), None)
                    if job:
                        st.markdown(f"Next check: {job.next_run_time}")

        # Notification Settings
        st.subheader("🔔 Notification Preferences")
        with st.expander("Configure Notifications", expanded=False):
            notification_email = st.text_input(
                "Email for notifications",
                key="dashboard_email",
                value=notifier.email_recipient if notifier.email_recipient else "",
                help="Enter your email to receive change notifications"
            )

            if st.button("Save Notification Settings"):
                notifier.set_email(notification_email)
                st.success("Notification settings saved!")

        # Change Analytics
        st.subheader("📊 Change Analytics")
        if all_changes:
            # Convert changes to DataFrame for analysis
            changes_df = pd.DataFrame([
                {
                    'timestamp': datetime.fromisoformat(c['timestamp']),
                    'type': c['type'],
                    'url': c['url']
                }
                for c in all_changes
            ])

            # Group changes by date and type
            daily_changes = changes_df.groupby([
                changes_df['timestamp'].dt.date,
                'type'
            ]).size().unstack(fill_value=0)

            # Plot changes over time
            st.line_chart(daily_changes)

            # Show change distribution
            st.bar_chart(changes_df['type'].value_counts())


with tab2:
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

            # Add toggle for crawling all pages
            crawl_all_pages = st.toggle(
                "Monitor all pages",
                help="When enabled, the system will automatically discover and monitor all pages under this domain.",
                key="crawl_all_pages"
            )

            if st.form_submit_button("Add Website"):
                if new_url:
                    website_config = {
                        "url": new_url,
                        "frequency": check_frequency,
                        "crawl_all_pages": crawl_all_pages,
                        "added_at": datetime.now().isoformat()
                    }
                    data_manager.store_website_config(website_config)

                    # Add to scheduler with normalized job ID
                    freq_map = {
                        "1 hour": 3600,
                        "6 hours": 21600,
                        "12 hours": 43200,
                        "24 hours": 86400
                    }

                    job_id = f"check_{_normalize_job_id(new_url)}"
                    scheduler.add_job(
                        check_website,
                        'interval',
                        seconds=freq_map[check_frequency],
                        id=job_id,
                        args=[new_url, crawl_all_pages]
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
                try:
                    # Remove scheduler job with normalized ID
                    job_id = f"check_{_normalize_job_id(website['url'])}"
                    try:
                        scheduler.remove_job(job_id)
                    except Exception as e:
                        st.warning(f"Note: Scheduler job was already removed or not found")

                    # Remove website config
                    data_manager.delete_website_config(website['url'])
                    st.success(f"Successfully removed {website['url']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error removing website: {str(e)}")

with tab3:
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
                check_website(website['url'], website.get('crawl_all_pages', False))
            st.success("All checks completed!")

    # Show monitoring status
    st.subheader("Monitoring Status")
    for job in scheduler.get_jobs():
        st.write(f"Next check for {job.args[0]}: {job.next_run_time}")

with tab4:
    # Demo section
    st.header("Change Visualization Demo")
    st.write("Here's an example of how changes are visualized when detected:")

    # Generate demo changes with varied significance scores
    if st.button("Generate Demo Changes"):
        demo_changes = [
            {
                'type': 'text_change',
                'location': 'Homepage',
                'before': 'Welcome to our store',
                'after': 'Welcome to our updated store',
                'url': 'https://demo-store.com',
                'timestamp': (datetime.now() - timedelta(days=2)).isoformat(),
                'significance_score': 3,  # Low significance
                'analysis': {
                    'explanation': 'Minor text update',
                    'impact_category': 'Content',
                    'business_relevance': 'Low',
                    'recommendations': 'No action needed'
                }
            },
            {
                'type': 'menu_structure_change',
                'location': 'Navigation Menu',
                'before': '- Home\n- Products\n- Contact',
                'after': '- Home\n- Products\n- About Us\n- Contact',
                'url': 'https://demo-store.com',
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'significance_score': 6,  # Medium-high significance
                'analysis': {
                    'explanation': 'Navigation structure modified',
                    'impact_category': 'Structure',
                    'business_relevance': 'Medium',
                    'recommendations': 'Update sitemap'
                }
            },
            {
                'type': 'text_change',
                'location': 'Product Page',
                'before': 'Original product description',
                'after': 'Updated product description with new features and pricing',
                'url': 'https://demo-store.com/products',
                'timestamp': datetime.now().isoformat(),
                'significance_score': 9,  # Critical significance
                'analysis': {
                    'explanation': 'Product pricing changed',
                    'impact_category': 'Content',
                    'business_relevance': 'High',
                    'recommendations': 'Update marketing materials'
                }
            }
        ]

        # Store the demo changes
        for change in demo_changes:
            data_manager.store_changes([change], change['url'])

        st.success("Demo changes generated with varying significance levels! Check the Timeline tab to view them.")

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