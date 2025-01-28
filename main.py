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
            # Clear previous content to force new crawl
            change_detector.previous_content = None

            # Perform the crawl
            current_content = scraper.scrape_website(url, crawl_all_pages)

            # Detect changes
            changes = change_detector.detect_changes(current_content)

            # Always store the current content as a change to track pages
            if not changes:
                changes = [{
                    'type': 'site_check',
                    'location': '/',
                    'timestamp': datetime.now().isoformat(),
                    'pages': current_content.get('pages', []),
                    'url': url
                }]

            # Store changes
            data_manager.store_changes(changes, url)

            if len(changes) > 1:  # More than just the site_check
                st.success(f"Found {len(changes)-1} changes on {url}")
            else:
                st.info(f"No changes detected on {url}")

            # Force streamlit to rerun to show updated data
            st.rerun()

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
                        <p><strong>Full Site Crawling:</strong> {'✅ Enabled' if website.get('crawl_all_pages', False) else '❌ Disabled'}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Crawler Status and Debug
                    st.markdown("### 🕷️ Crawler Status")

                    # Force new crawl button
                    if st.button("Force New Crawl", key=f"force_crawl_{website['url']}"):
                        with st.spinner("Starting new crawl..."):
                            try:
                                # Clear previous content to force new crawl
                                change_detector.previous_content = None
                                # Run crawler
                                check_website(website['url'], website.get('crawl_all_pages', False))
                                st.success("Crawl completed!")
                            except Exception as e:
                                st.error(f"Crawl failed: {str(e)}")

                    # Show crawled pages if full site crawling is enabled
                    if website.get('crawl_all_pages', False):
                        recent_changes = [c for c in all_changes if c['url'] == website['url']]
                        if recent_changes:
                            st.markdown("### 📑 Crawled Pages")

                            # Create tabs for different views
                            page_tabs = st.tabs(["Pages List", "Crawl Stats", "Debug Info"])

                            with page_tabs[0]:
                                monitored_pages = set()
                                for change in recent_changes:
                                    if 'pages' in change:
                                        for page in change['pages']:
                                            if isinstance(page, dict):
                                                url = page.get('url', 'Unknown')
                                                location = page.get('location', 'Unknown')
                                                monitored_pages.add((url, location))

                                if monitored_pages:
                                    st.markdown("The following pages were discovered and are being monitored:")
                                    for url, location in sorted(monitored_pages):
                                        st.markdown(f"""
                                        <div style='border-left: 3px solid #1f77b4; padding: 10px; margin: 10px 0; background-color: #f8f9fa;'>
                                            <p style='margin: 0;'><strong>{location}</strong></p>
                                            <p style='margin: 0; color: #666;'><small>{url}</small></p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    st.warning("No pages have been discovered yet. Try forcing a new crawl.")

                            with page_tabs[1]:
                                st.markdown("### Crawling Statistics")
                                latest_change = recent_changes[-1]
                                if 'pages' in latest_change:
                                    num_pages = len(latest_change['pages'])
                                    st.metric("Total Pages Crawled", num_pages)

                                    # Show timestamp of last crawl
                                    last_crawl = datetime.fromisoformat(latest_change['timestamp'].replace('Z', '+00:00'))
                                    st.metric("Last Crawl", last_crawl.strftime('%Y-%m-%d %H:%M:%S'))
                                else:
                                    st.warning("No crawling statistics available yet.")

                            with page_tabs[2]:
                                st.markdown("### 🔍 Debug Information")
                                st.write("Recent Changes Data:", recent_changes)
                                st.write("Pages Found:", monitored_pages if 'monitored_pages' in locals() else "No pages data")

                                # Show crawler logs
                                if st.checkbox("Show Crawler Logs", key=f"show_logs_{website['url']}"):
                                    st.code("\n".join(str(log) for log in scraper.get_logs()))
                        else:
                            st.warning("No crawl data available. Try forcing a new crawl.")

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
                                  if job.id == f"check_{_normalize_job_id(website['url'])}"), None)
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
    st.header("Website Changes Timeline")
    changes = data_manager.get_recent_changes()

    if not changes:
        st.info("No changes detected yet. Changes will appear here once detected.")
    else:
        # Group changes by date
        changes_by_date = {}
        for change in changes:
            date = datetime.fromisoformat(change['timestamp']).date()
            if date not in changes_by_date:
                changes_by_date[date] = []
            changes_by_date[date].append(change)

        # Display changes grouped by date
        for date in sorted(changes_by_date.keys(), reverse=True):
            with st.expander(f"📅 {date}", expanded=True):
                for change in changes_by_date[date]:
                    # Create a card-like container for each change
                    with st.container():
                        # Header with timestamp and type
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            change_time = datetime.fromisoformat(change['timestamp']).strftime('%H:%M:%S')
                            change_type = change['type'].replace('_', ' ').title()
                            st.markdown(f"### 🕒 {change_time} - {change_type}")
                            st.markdown(f"**URL:** {change['url']}")
                            if 'location' in change:
                                st.markdown(f"**Location:** {change['location']}")

                        with col2:
                            # Show significance score if available
                            if 'significance_score' in change:
                                score = change['significance_score']
                                color = 'red' if score >= 8 else 'orange' if score >= 5 else 'green'
                                st.markdown(f"""
                                    <div style='text-align: right;'>
                                        <span style='color: {color}; font-size: 1.2em;'>
                                            Significance: {score}/10
                                        </span>
                                    </div>
                                """, unsafe_allow_html=True)

                        # Show change details based on type
                        if change['type'] in ['text_change', 'menu_structure_change']:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Before:**")
                                st.text_area("", value=change.get('before', ''), height=150, 
                                           key=f"before_{change['timestamp']}", disabled=True)
                            with col2:
                                st.markdown("**After:**")
                                st.text_area("", value=change.get('after', ''), height=150, 
                                           key=f"after_{change['timestamp']}", disabled=True)

                        elif change['type'] in ['links_added', 'links_removed']:
                            st.markdown("**Changed Links:**")
                            st.text_area("", value=change.get('after', '') or change.get('before', ''), 
                                       height=100, key=f"links_{change['timestamp']}", disabled=True)

                        elif change['type'] == 'visual_change' and 'diff_image' in change:
                            st.markdown("**Visual Changes:**")
                            st.image(change['diff_image'], caption="Visual differences highlighted", 
                                   use_column_width=True)

                        # Show AI analysis if available
                        if 'analysis' in change:
                            with st.expander("🤖 AI Analysis", expanded=False):
                                analysis = change['analysis']
                                st.markdown(f"""
                                    - **Impact:** {analysis.get('explanation', 'N/A')}
                                    - **Category:** {analysis.get('impact_category', 'N/A')}
                                    - **Business Relevance:** {analysis.get('business_relevance', 'N/A')}
                                    - **Recommendations:** {analysis.get('recommendations', 'N/A')}
                                """)

                        st.divider()  # Add visual separator between changes

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

    st.info("Click the 'Generate Demo Changes' button above to create sample changes with different significance levels, "
            "then go to the Timeline tab to see how changes are visualized with color-coding based on their significance.")