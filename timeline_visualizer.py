import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from diff_visualizer import DiffVisualizer

class TimelineVisualizer:
    def __init__(self):
        self.diff_visualizer = DiffVisualizer(key_prefix="timeline")

    def _prepare_timeline_data(self, changes: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert changes data to a DataFrame for timeline visualization"""
        timeline_data = []
        for change in changes:
            timeline_data.append({
                'timestamp': datetime.fromisoformat(change['timestamp']),
                'type': change['type'],
                'location': change['location'],
                'url': change.get('url', 'Unknown'),
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

        # Date filter
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()

        start_date = st.date_input(
            "From date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

        end_date = st.date_input(
            "To date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

        # Filter by date
        mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
        filtered_df = df.loc[mask]

        # Display timeline overview
        st.subheader("Timeline Overview")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Changes", len(filtered_df))
        with col2:
            st.metric("Time Range", f"{(end_date - start_date).days + 1} days")

        # Show changes over time
        st.subheader("Changes Over Time")
        timeline_data = filtered_df.copy()
        timeline_data['date'] = timeline_data['timestamp'].dt.date
        daily_changes = timeline_data.groupby('date').size().reset_index(name='count')
        st.line_chart(data=daily_changes.set_index('date'))

        # Display individual changes
        st.subheader("Change Details")
        for idx, change in filtered_df.iterrows():
            change_data = change['change_data']
            with st.expander(
                f"{self._get_change_icon(change['type'])} {change['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {change['type'].replace('_', ' ').title()}"
            ):
                st.write(f"**Location:** {change['location']}")
                st.write(f"**URL:** {change['url']}")

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