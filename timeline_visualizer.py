import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from diff_visualizer import DiffVisualizer

class TimelineVisualizer:
    def __init__(self):
        self.diff_visualizer = DiffVisualizer(key_prefix="timeline")
        # Define color scheme for significance levels
        self.significance_colors = {
            'critical': '#FF4B4B',  # Red for high significance (8-10)
            'high': '#FFA726',      # Orange for medium-high (6-7)
            'medium': '#FDD835',    # Yellow for medium (4-5)
            'low': '#66BB6A'        # Green for low (1-3)
        }

    def _get_significance_color(self, score: int) -> str:
        """Return color based on significance score"""
        if score >= 8:
            return self.significance_colors['critical']
        elif score >= 6:
            return self.significance_colors['high']
        elif score >= 4:
            return self.significance_colors['medium']
        else:
            return self.significance_colors['low']

    def _get_significance_label(self, score: int) -> str:
        """Return significance label based on score"""
        if score >= 8:
            return "Critical"
        elif score >= 6:
            return "High"
        elif score >= 4:
            return "Medium"
        else:
            return "Low"

    def _show_significance_legend(self):
        """Display a legend explaining significance colors"""
        st.markdown("#### 📊 Change Significance Legend")
        cols = st.columns(4)
        for i, (level, color) in enumerate(self.significance_colors.items()):
            with cols[i]:
                st.markdown(
                    f'<div style="background-color: {color}; padding: 10px; '
                    f'border-radius: 5px; color: {"black" if level in ["medium", "low"] else "white"}; '
                    f'text-align: center;">{level.title()}</div>',
                    unsafe_allow_html=True
                )

    def _prepare_timeline_data(self, changes: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert changes data to a DataFrame for timeline visualization"""
        timeline_data = []
        for change in changes:
            timeline_data.append({
                'timestamp': datetime.fromisoformat(change['timestamp']),
                'type': change['type'],
                'location': change['location'],
                'url': change.get('url', 'Unknown'),
                'page_name': change.get('location', '').split('/')[-1] or 'Homepage',
                'significance': change.get('significance_score', 0),
                'change_data': change
            })
        return pd.DataFrame(timeline_data)

    def _get_change_icon(self, change_type: str) -> str:
        """Return an emoji icon based on change type"""
        icons = {
            'text_change': '📝',
            'links_added': '🔗',
            'links_removed': '❌',
            'visual_change': '🖼️',
            'menu_structure_change': '📑',
            'styles_added': '🎨',
            'styles_removed': '🎨',
            'fonts_added': '📰',
            'fonts_removed': '📰',
            'colors_added': '🎨',
            'colors_removed': '🎨'
        }
        return icons.get(change_type, '📄')

    def visualize_timeline(self, changes: List[Dict[str, Any]]):
        """Create an interactive timeline visualization of changes"""
        if not changes:
            st.info("No changes to display in the timeline.")
            return

        # Convert changes to DataFrame for easier manipulation
        df = self._prepare_timeline_data(changes)

        # Timeline header
        st.title("📅 Website Changes Timeline")

        # Show significance legend
        self._show_significance_legend()

        # Website and page selection
        unique_websites = df['url'].unique()
        if len(unique_websites) > 0:
            selected_website = st.selectbox(
                "Select Website",
                options=unique_websites,
                key="timeline_website_selector"
            )

            # Filter data for selected website
            website_df = df[df['url'] == selected_website]

            # Get unique pages for the selected website
            unique_pages = sorted(website_df['page_name'].unique())
            page_options = ['All Pages'] + list(unique_pages)
            selected_page = st.selectbox(
                "Select Page",
                options=page_options,
                key="timeline_page_selector"
            )

            # Filter based on page selection
            if selected_page != 'All Pages':
                filtered_df = website_df[website_df['page_name'] == selected_page]
            else:
                filtered_df = website_df

            # Page overview if "All Pages" is selected
            if selected_page == 'All Pages':
                st.subheader("📑 Pages Overview")
                page_stats = website_df.groupby('page_name').agg({
                    'type': 'count',
                    'significance': 'mean',
                    'timestamp': ['min', 'max']
                }).reset_index()
                page_stats.columns = ['Page', 'Changes', 'Avg Significance', 'First Change', 'Last Change']

                # Display page statistics with color coding
                for _, row in page_stats.iterrows():
                    significance_color = self._get_significance_color(int(row['Avg Significance']))
                    with st.expander(
                        f"📄 {row['Page']} ({row['Changes']} changes)", 
                        expanded=False
                    ):
                        st.markdown(
                            f'<div style="border-left: 5px solid {significance_color}; padding-left: 10px;">'
                            f'<p><strong>Average Significance:</strong> {row["Avg Significance"]:.1f} '
                            f'({self._get_significance_label(int(row["Avg Significance"]))})</p>'
                            f'<p><strong>First Change:</strong> {row["First Change"]}</p>'
                            f'<p><strong>Last Change:</strong> {row["Last Change"]}</p>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                st.divider()

            # Display individual changes with color coding
            st.subheader("Change Details")
            for idx, change in filtered_df.iterrows():
                change_data = change['change_data']
                significance_color = self._get_significance_color(int(change['significance']))
                significance_label = self._get_significance_label(int(change['significance']))

                expander_label = (
                    f"{self._get_change_icon(change['type'])} "
                    f"{change['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - "
                    f"{change['type'].replace('_', ' ').title()}"
                )

                with st.expander(expander_label):
                    st.markdown(
                        f'<div style="border-left: 5px solid {significance_color}; padding-left: 10px;">'
                        f'<p><strong>Significance:</strong> {change["significance"]} ({significance_label})</p>'
                        f'<p><strong>Location:</strong> {change["location"]}</p>'
                        f'<p><strong>URL:</strong> {change["url"]}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    if change['type'] == 'visual_change':
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write("Before:")
                            st.image(change_data['before_image'])
                        with col2:
                            st.write("After:")
                            st.image(change_data['after_image'])
                        with col3:
                            st.write("Difference:")
                            st.image(change_data['diff_image'])
                    else:
                        diff_viz = DiffVisualizer(key_prefix=f"change_{idx}")
                        diff_viz.visualize_diff(
                            change_data.get('before', ''),
                            change_data.get('after', '')
                        )

            # Show changes over time with significance
            st.subheader("Changes Over Time")
            timeline_data = filtered_df.copy()
            timeline_data['date'] = timeline_data['timestamp'].dt.date

            # Create significance categories for visualization
            timeline_data['significance_category'] = timeline_data['significance'].apply(self._get_significance_label)

            # Group by date and significance category
            daily_changes = timeline_data.groupby(['date', 'significance_category']).size().unstack(fill_value=0)
            st.bar_chart(daily_changes)

        self._render_comparison_view(df)
        self._render_analytics_view(df)

    def _render_comparison_view(self, df: pd.DataFrame):
        """Render the comparison view tab"""
        st.markdown("### Compare Changes Across Time")

        # Filter options for comparison
        url_to_compare = st.selectbox(
            "Select Website to Compare",
            options=list(df['url'].unique()),
            key="timeline_compare_url"
        )

        # Filter changes for selected URL
        url_changes = df[df['url'] == url_to_compare]

        # Create two columns for selecting timestamps
        col1, col2 = st.columns(2)
        with col1:
            timestamp1 = st.selectbox(
                "Select First Timestamp",
                options=url_changes['timestamp'],
                format_func=lambda x: x.strftime('%Y-%m-%d %H:%M:%S'),
                key="timeline_timestamp1"
            )

        if timestamp1:
            with col2:
                # Only show timestamps after the first selected timestamp
                later_timestamps = url_changes[url_changes['timestamp'] > timestamp1]['timestamp']
                timestamp2 = st.selectbox(
                    "Select Second Timestamp",
                    options=later_timestamps,
                    format_func=lambda x: x.strftime('%Y-%m-%d %H:%M:%S'),
                    key="timeline_timestamp2"
                )

                if timestamp2:
                    # Get the change data for both timestamps
                    change1 = url_changes[url_changes['timestamp'] == timestamp1].iloc[0]['change_data']
                    change2 = url_changes[url_changes['timestamp'] == timestamp2].iloc[0]['change_data']

                    st.markdown("### Comparison Results")

                    # Create a unique diff visualizer for the comparison
                    comparison_diff = DiffVisualizer(
                        key_prefix=f"comparison_{timestamp1.strftime('%Y%m%d%H%M%S')}_{timestamp2.strftime('%Y%m%d%H%M%S')}"
                    )

                    # Display comparison based on change type
                    if change1['type'] == 'visual_change' and change2['type'] == 'visual_change':
                        cols = st.columns(2)
                        with cols[0]:
                            st.write(f"State at {timestamp1.strftime('%Y-%m-%d %H:%M:%S')}")
                            st.image(f"data:image/png;base64,{change1['after_image']}")
                        with cols[1]:
                            st.write(f"State at {timestamp2.strftime('%Y-%m-%d %H:%M:%S')}")
                            st.image(f"data:image/png;base64,{change2['after_image']}")
                    else:
                        st.write("Content Changes Between Selected Times:")
                        comparison_diff.visualize_diff(
                            change1.get('after', ''),
                            change2.get('after', '')
                        )

    def _render_analytics_view(self, df: pd.DataFrame):
        """Render the analytics view tab"""
        st.markdown("### Change Analytics")

        # Time-based analysis
        st.markdown("#### Change Frequency Over Time")
        df['date'] = df['timestamp'].dt.date
        daily_changes = df.groupby('date').size()
        st.line_chart(daily_changes)

        # Change type distribution
        st.markdown("#### Change Type Distribution")
        type_dist = df['type'].value_counts()
        st.bar_chart(type_dist)

        # Significance distribution
        st.markdown("#### Significance Score Distribution")
        significance_dist = df['significance'].value_counts().sort_index()
        st.bar_chart(significance_dist)

        # Website activity
        if 'url' in df.columns:
            st.markdown("#### Website Activity")
            website_activity = df['url'].value_counts()
            st.bar_chart(website_activity)