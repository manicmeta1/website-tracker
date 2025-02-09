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
from change_summarizer import ChangeSummarizer

def _normalize_job_id(url: str) -> str:
    """Normalize URL for job ID to ensure consistency"""
    return url.replace('https://', '').replace('http://', '').strip('/')

async def check_website(url: str, crawl_all_pages: bool = False): #Updated to async
    """Perform website check and detect changes"""
    try:
        # Create a progress container with animation
        progress_container = st.empty()
        status_container = st.empty()

        with st.spinner(f"🔍 Scanning {url}..."):
            # Clear previous content to force new crawl
            change_detector.previous_content = None

            # Create animated progress bar
            progress_bar = progress_container.progress(0)
            status_container.markdown("""
                <div class='status-active'>
                    ⚡ Starting website scan...
                </div>
            """, unsafe_allow_html=True)

            def progress_callback(current, total, elapsed_time):
                # Update progress bar with animation
                progress_percentage = min(current / max(total, 1) * 100, 100)
                progress_container.markdown(f"""
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar progress-bar-animated" 
                             role="progressbar" 
                             style="width: {progress_percentage}%">
                            {int(progress_percentage)}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Update status message with emoji indicators
                status = "🔍" if current < total else "✅"
                status_container.markdown(f"""
                    <div class='status-active'>
                        {status} Scanned {current} out of {total} pages<br>
                        ⏱️ Time elapsed: {int(elapsed_time)} seconds
                    </div>
                """, unsafe_allow_html=True)

            # Perform the crawl with progress callback
            current_content = scraper.scrape_website(url, crawl_all_pages, progress_callback)

            # Clear progress displays with fade-out effect
            progress_container.empty()
            status_container.empty()

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

            # Analyze changes with AI if there are meaningful changes
            if len(changes) > 1:  # More than just the site_check
                try:
                    analyzed_changes = await change_summarizer.analyze_changes(changes)
                    changes = analyzed_changes
                except Exception as e:
                    st.warning(f"⚠️ AI analysis unavailable: {str(e)}")

            # Store changes with visual feedback
            data_manager.store_changes(changes, url)

            if len(changes) > 1:  # More than just the site_check
                st.markdown(f"""
                    <div class='change-highlight'>
                        ✨ Found {len(changes)-1} changes on {url}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.info(f"👀 No changes detected on {url}")

            # Force streamlit to rerun to show updated data
            st.rerun()

    except Exception as e:
        st.error(f"❌ Error checking website: {str(e)}")

# Initialize components
data_manager = DataManager()
scraper = WebScraper()
change_detector = ChangeDetector()
notifier = EmailNotifier()
diff_visualizer = DiffVisualizer(key_prefix="demo")
timeline_visualizer = TimelineVisualizer()
change_summarizer = ChangeSummarizer() # Add to the Initialize components section after line 101

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Streamlit UI
st.set_page_config(layout="wide", page_title="Website Monitor")

# Update the CSS section to add animation styles
st.markdown("""
<style>
    .metric-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1rem;
        background-color: white;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-active {
        color: #28a745;
        animation: pulse 2s infinite;
    }
    .status-inactive {
        color: #dc3545;
    }
    .notification-settings {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    .progress-bar-animated {
        background: linear-gradient(45deg, 
            rgba(31,119,180,0.8) 25%, 
            rgba(31,119,180,1) 50%, 
            rgba(31,119,180,0.8) 75%);
        background-size: 200% 100%;
        animation: progress-animation 2s linear infinite;
    }
    @keyframes progress-animation {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    .change-highlight {
        animation: highlight 1s ease-in-out;
    }
    @keyframes highlight {
        0% { background-color: rgba(255,243,205,1); }
        100% { background-color: rgba(255,243,205,0); }
    }
</style>
""", unsafe_allow_html=True)

# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dashboard", "Website Management", "Change Timeline", "Demo", "Preferences"])

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
                                st.experimental_run(check_website, args=(website['url'], website.get('crawl_all_pages', False))) #Run async function
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
                                    # Group pages by their root path for better organization
                                    grouped_pages = {}
                                    for url, location in sorted(monitored_pages):
                                        root_path = location.split('/')[1] if location.startswith('/') and len(location.split('/')) > 1 else 'Main'
                                        if root_path not in grouped_pages:
                                            grouped_pages[root_path] = []
                                        grouped_pages[root_path].append((url, location))

                                    st.markdown("### 📑 Discovered Pages by Section")

                                    # Display sections using containers to avoid nesting issues
                                    for group_name, pages in grouped_pages.items():
                                        group_container = st.container()

                                        # Use checkbox for collapsible behavior
                                        is_expanded = st.checkbox(
                                            f"📁 {group_name.capitalize()} Section - {len(pages)} pages",
                                            key=f"section_{website['url']}_{group_name}"
                                        )

                                        if is_expanded:
                                            with group_container:
                                                # Display pages in a table-like layout
                                                for url, location in pages:
                                                    st.markdown(f"""
                                                    <div style='display: flex; justify-content: space-between; 
                                                                 padding: 8px; margin: 4px 0; 
                                                                 background-color: #f8f9fa; border-radius: 4px;'>
                                                        <div style='flex: 1;'><strong>{location}</strong></div>
                                                        <div style='flex: 2; color: #666;'><code>{url}</code></div>
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
                                # Debug information with toggles instead of nested expanders
                                st.markdown("### 🔍 Debug Information")

                                # Use checkboxes for collapsible sections
                                if st.checkbox("Show Change Data", key=f"show_changes_{website['url']}"):
                                    st.json(recent_changes)

                                if st.checkbox("Show Pages Data", key=f"show_pages_{website['url']}"):
                                    st.json(list(monitored_pages) if 'monitored_pages' in locals() else "No pages data")

                                if st.checkbox("Show Crawler Logs", key=f"show_logs_{website['url']}"):
                                    st.code("\n".join(str(log) for log in scraper.get_logs()))

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
                            st.experimental_run(check_website, args=(website['url'], website.get('crawl_all_pages', False))) #Run async function

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

def generate_timeline_demo_changes():
    """Generate demo changes for timeline visualization"""
    return [
        {
            'type': 'text_change',
            'location': 'Homepage',
            'before': 'Welcome to Edica Naturals - Your Source for Natural Menopause Relief',
            'after': 'Welcome to Edica Naturals - Advanced Natural Solutions for Menopause Relief',
            'url': 'edicanaturals.com',
            'timestamp': datetime.now().isoformat(),
            'significance_score': 6,
            'analysis': {
                'explanation': 'Homepage messaging updated to emphasize product sophistication',
                'impact_category': 'Marketing',
                'business_relevance': 'Medium',
                'recommendations': 'Update social media profiles with new messaging'
            }
        },
        {
            'type': 'menu_structure_change',
            'location': 'Navigation Menu',
            'before': '- Home\n- Products\n- About\n- Contact',
            'after': '- Home\n- Products\n- Research\n- About\n- Contact',
            'url': 'edicanaturals.com',
            'timestamp': datetime.now().isoformat(),
            'significance_score': 8,
            'analysis': {
                'explanation': 'Added new Research section to main navigation',
                'impact_category': 'Structure',
                'business_relevance': 'High',
                'recommendations': 'Ensure new research section has proper content and tracking'
            }
        }
    ]

with tab3:
    st.header("Website Changes Timeline")

    # Initialize diff visualizer for timeline
    timeline_diff_viz = DiffVisualizer(key_prefix="timeline")

    # Add view mode selection
    diff_view_mode = st.radio(
        "Diff View Mode",
        ["Side by Side", "Inline"],
        key="timeline_diff_view_mode",
        horizontal=True
    )

    # Use a session state to manage demo data loading
    if 'demo_data_loaded' not in st.session_state:
        st.session_state.demo_data_loaded = False

    # Make demo data generation more prominent
    st.info("👉 Click the button below to see example changes with visual formatting")

    if st.button("🎯 Load Example Timeline Data", key="demo_timeline"):
        try:
            demo_changes = generate_timeline_demo_changes()
            data_manager.store_changes(demo_changes, 'edicanaturals.com')
            st.session_state.demo_data_loaded = True
            st.success("✅ Demo data loaded! You should now see the changes below.")
        except Exception as e:
            st.error(f"Failed to load demo data: {str(e)}")
            st.session_state.demo_data_loaded = False

    # Add website filter dropdown
    websites = data_manager.get_website_configs()
    website_urls = ["All Websites"] + [w['url'] for w in websites]
    selected_website = st.selectbox("Select Website", website_urls)

    try:
        # Get changes, filtered by selected website if needed
        if selected_website == "All Websites":
            changes = data_manager.get_recent_changes()
        else:
            changes = data_manager.get_recent_changes(url=selected_website)

        if not changes:
            st.warning("No changes detected yet. Click '🎯 Load Example Timeline Data' above to see example changes.")
        else:
            # Create a container for the timeline content
            timeline_container = st.container()

            with timeline_container:
                # Group changes by website
                grouped_changes = {}
                for change in changes:
                    if change['type'] == 'site_check':
                        continue

                    website = change['url']
                    if website not in grouped_changes:
                        grouped_changes[website] = []
                    grouped_changes[website].append(change)

                # Display changes grouped by website
                for website, website_changes in grouped_changes.items():
                    st.markdown(f"""
                        <div style='padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6; margin-bottom: 1rem;'>
                            <h2 style='margin: 0;'>🌐 {website}</h2>
                        </div>
                    """, unsafe_allow_html=True)

                    # Create a container for all changes in this website
                    website_container = st.container()

                    with website_container:
                        for change in website_changes:
                            # Use a unique key for each change element
                            change_key = f"{website}_{change['timestamp']}_{change['type']}"

                            with st.container():
                                st.markdown(f"""
                                    <div style='background-color: #ffffff; padding: 1rem; border-radius: 0.5rem; 
                                            margin-bottom: 1rem; border: 1px solid #dee2e6;'>
                                        <h4 style='margin: 0; color: #1f77b4;'>{change['type'].replace('_', ' ').title()}</h4>
                                        <p style='margin: 0.5rem 0 0 0; color: #666;'>
                                            <strong>Location:</strong> {change['location']}
                                        </p>
                                    </div>
                                """, unsafe_allow_html=True)

                                # Show change content with enhanced diff visualization
                                if change['type'] in ['text_change', 'menu_structure_change']:
                                    if 'before' in change and 'after' in change:
                                        # Use the DiffVisualizer to show changes
                                        if diff_view_mode == "Side by Side":
                                            left_diff, right_diff = timeline_diff_viz.create_side_by_side_diff(
                                                change['before'],
                                                change['after']
                                            )
                                            cols = st.columns(2)
                                            with cols[0]:
                                                st.markdown("**Before:**")
                                                st.markdown(left_diff, unsafe_allow_html=True)
                                            with cols[1]:
                                                st.markdown("**After:**")
                                                st.markdown(right_diff, unsafe_allow_html=True)
                                        else:
                                            st.markdown("**Changes:**")
                                            inline_diff = timeline_diff_viz.create_inline_diff(
                                                change['before'],
                                                change['after']
                                            )
                                            st.markdown(inline_diff, unsafe_allow_html=True)

                                        # Show diff statistics
                                        stats = timeline_diff_viz.get_diff_stats(change['before'], change['after'])
                                        stat_cols = st.columns(3)
                                        with stat_cols[0]:
                                            st.metric("Words Added", stats['words_added'])
                                        with stat_cols[1]:
                                            st.metric("Words Removed", stats['words_removed'])
                                        with stat_cols[2]:
                                            st.metric("Total Changes", stats['total_changes'])

                                # Show AI analysis if available
                                if 'analysis' in change:
                                    with st.expander("🤖 View AI Analysis", expanded=False):
                                        analysis = change['analysis']
                                        st.markdown(f"""
                                            <div class='analysis-content'>
                                                <p><strong>Impact:</strong> {analysis.get('explanation', 'N/A')}</p>
                                                <p><strong>Category:</strong> {analysis.get('impact_category', 'N/A')}</p>
                                                <p><strong>Business Relevance:</strong> {analysis.get('business_relevance', 'N/A')}</p>
                                                <p><strong>Recommendations:</strong> {analysis.get('recommendations', 'N/A')}</p>
                                            </div>
                                        """, unsafe_allow_html=True)

                                st.markdown("<hr>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading timeline data: {str(e)}")

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

with tab5:
    st.title("🎛️ Monitoring Preferences")

    # Get current preferences
    current_preferences = data_manager.get_preferences()

    st.header("Global Preferences")

    # Notification Preferences
    st.subheader("📨 Notification Settings")
    notification_prefs = current_preferences.get("notification_preferences", {})

    email_notifications = st.toggle(
        "Enable Email Notifications",
        value=notification_prefs.get("email_notifications", True),
        help="Receive email notifications for website changes"
    )

    min_significance = st.slider(
        "Minimum Change Significance for Notifications",
        min_value=1,
        max_value=10,
        value=notification_prefs.get("minimum_significance", 5),
        help="Only notify for changes with significance above this threshold"
    )

    notification_frequency = st.selectbox(
        "Notification Frequency",
        options=["immediate", "hourly", "daily", "weekly"],
        index=["immediate", "hourly", "daily", "weekly"].index(
            notification_prefs.get("notification_frequency", "immediate")
        ),
        help="How often to receive notifications"
    )

    # Monitoring Preferences
    st.subheader("🔍 Monitoring Settings")
    monitoring_prefs = current_preferences.get("monitoring_preferences", {})

    default_frequency = st.selectbox(
        "Default Check Frequency",
        options=["1 hour", "6 hours", "12 hours", "24 hours"],
        index=["1 hour", "6 hours", "12 hours", "24 hours"].index(
            monitoring_prefs.get("default_check_frequency", "6 hours")
        ),
        help="Default monitoring frequency for new websites"
    )

    crawl_all_pages_default = st.toggle(
        "Monitor All Pages by Default",
        value=monitoring_prefs.get("crawl_all_pages_default", False),
        help="When enabled, new websites will be monitored across all pages by default"
    )

    # Display Preferences
    st.subheader("🎨 Display Settings")
    display_prefs = current_preferences.get("display_preferences", {})

    default_diff_view = st.radio(
        "Default Diff View",
        options=["side-by-side", "inline"],
        index=0 if display_prefs.get("default_diff_view", "side-by-side") == "side-by-side" else 1,
        horizontal=True,
        help="Choose how to display content changes"
    )

    color_scheme = st.selectbox(
        "Color Scheme",
        options=["default", "dark", "pastel"],
        index=["default", "dark", "pastel"].index(
            display_prefs.get("color_scheme", "default")
        ),
        help="Choose the color scheme for the interface"
    )

    # Save preferences button
    if st.button("Save Preferences", type="primary"):
        try:
            new_preferences = {
                "notification_preferences": {
                    "email_notifications": email_notifications,
                    "minimum_significance": min_significance,
                    "notification_frequency": notification_frequency
                },
                "monitoring_preferences": {
                    "default_check_frequency": default_frequency,
                    "crawl_all_pages_default": crawl_all_pages_default
                },
                "display_preferences": {
                    "default_diff_view": default_diff_view,
                    "color_scheme": color_scheme
                }
            }

            data_manager.store_preferences(new_preferences)
            st.success("✅ Preferences saved successfully!")

            # Rerun to apply new preferences
            st.rerun()

        except Exception as e:
            st.error(f"Failed to save preferences: {str(e)}")

    # Individual Website Preferences
    st.header("Website-Specific Preferences")
    websites = data_manager.get_website_configs()

    if not websites:
        st.info("No websites configured yet. Add websites in the Website Management tab.")
    else:
        for website in websites:
            with st.expander(f"🌐 {website['url']}", expanded=False):
                website_prefs = website.get('preferences', {})

                col1, col2 = st.columns(2)
                with col1:
                    custom_frequency = st.selectbox(
                        "Check Frequency",
                        options=["1 hour", "6 hours", "12 hours", "24 hours"],
                        index=["1 hour", "6 hours", "12 hours", "24 hours"].index(
                            website_prefs.get("check_frequency", website.get("frequency", "6 hours"))
                        ),
                        key=f"freq_{website['url']}"
                    )

                    custom_crawl = st.toggle(
                        "Monitor All Pages",
                        value=website_prefs.get("crawl_all_pages", website.get("crawl_all_pages", False)),
                        key=f"crawl_{website['url']}"
                    )

                with col2:
                    custom_min_significance = st.slider(
                        "Minimum Change Significance",
                        min_value=1,
                        max_value=10,
                        value=website_prefs.get("minimum_significance", min_significance),
                        key=f"sig_{website['url']}"
                    )

                if st.button("Save Website Preferences", key=f"save_{website['url']}"):
                    try:
                        website_preferences = {
                            "check_frequency": custom_frequency,
                            "crawl_all_pages": custom_crawl,
                            "minimum_significance": custom_min_significance
                        }
                        data_manager.update_website_preferences(website['url'], website_preferences)
                        st.success(f"✅ Preferences saved for {website['url']}")

                        # Update scheduler
                        job_id = f"check_{_normalize_job_id(website['url'])}"
                        freq_map = {
                            "1 hour": 3600,
                            "6 hours": 21600,
                            "12 hours": 43200,
                            "24 hours": 86400
                        }

                        # Update existing job
                        try:
                            scheduler.reschedule_job(
                                job_id,
                                trigger='interval',
                                seconds=freq_map[custom_frequency]
                            )
                        except Exception as e:
                            st.warning(f"Note: Scheduler job will be updated on next restart")

                    except Exception as e:
                        st.error(f"Failed to save preferences: {str(e)}")