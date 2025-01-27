import streamlit as st
import pandas as pd
from datetime import datetime
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
        st.markdown("### 📅 Website Changes Timeline")

        # Create tabs for different views
        tab1, tab2 = st.tabs(["Timeline View", "Comparison View"])

        with tab1:
            # Add filters for better navigation
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_url = st.selectbox(
                    "Filter by Website",
                    options=['All'] + list(df['url'].unique()),
                    key="timeline_url_filter"
                )
            with col2:
                selected_type = st.selectbox(
                    "Filter by Change Type",
                    options=['All'] + list(df['type'].unique()),
                    key="timeline_type_filter"
                )
            with col3:
                min_significance = st.slider(
                    "Minimum Significance Score",
                    min_value=1,
                    max_value=10,
                    value=1,
                    key="significance_filter"
                )

            # Apply filters
            filtered_df = df.copy()
            if selected_url != 'All':
                filtered_df = filtered_df[filtered_df['url'] == selected_url]
            if selected_type != 'All':
                filtered_df = filtered_df[filtered_df['type'] == selected_type]

            # Filter by significance score
            filtered_df = filtered_df[
                filtered_df['change_data'].apply(
                    lambda x: x.get('significance_score', 0) >= min_significance
                )
            ]

            # Group changes by date for the timeline
            filtered_df['date'] = filtered_df['timestamp'].dt.date
            dates = sorted(filtered_df['date'].unique())

            # Timeline visualization
            for date in dates:
                day_changes = filtered_df[filtered_df['date'] == date]
                with st.expander(f"📅 {date.strftime('%Y-%m-%d')} ({len(day_changes)} changes)", expanded=True):
                    for idx, change in day_changes.iterrows():
                        change_data = change['change_data']
                        significance_score = change_data.get('significance_score', 0)
                        analysis = change_data.get('analysis', {})

                        # Create unique prefix for each change entry
                        change_prefix = f"timeline_{change['timestamp'].strftime('%Y%m%d%H%M%S')}_{idx}"
                        diff_viz = DiffVisualizer(key_prefix=change_prefix)

                        # Enhanced card display with significance score
                        st.markdown(f"""
                        <div style='border:1px solid #ddd; border-radius:5px; padding:10px; margin:5px;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <h4>{self._get_change_icon(change['type'])} {change['type'].replace('_', ' ').title()}</h4>
                                <span style='background-color: {"#28a745" if significance_score >= 7 else "#ffc107" if significance_score >= 4 else "#dc3545"}; 
                                           color: white; padding: 5px 10px; border-radius: 15px;'>
                                    Significance: {significance_score}/10
                                </span>
                            </div>
                            <p><strong>Time:</strong> {change['timestamp'].strftime('%H:%M:%S')}</p>
                            <p><strong>URL:</strong> {change['url']}</p>
                            <p><strong>Location:</strong> {change['location']}</p>

                            <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;'>
                                <h5>AI Analysis</h5>
                                <p><strong>Impact Category:</strong> {analysis.get('impact_category', 'N/A')}</p>
                                <p><strong>Explanation:</strong> {analysis.get('explanation', 'N/A')}</p>
                                <p><strong>Business Relevance:</strong> {analysis.get('business_relevance', 'N/A')}</p>
                                <p><strong>Recommendations:</strong> {analysis.get('recommendations', 'N/A')}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Display the actual changes
                        if change['type'] == 'visual_change':
                            cols = st.columns(3)
                            with cols[0]:
                                st.write("Before:")
                                st.image(f"data:image/png;base64,{change_data['before_image']}")
                            with cols[1]:
                                st.write("After:")
                                st.image(f"data:image/png;base64,{change_data['after_image']}")
                            with cols[2]:
                                st.write("Differences:")
                                st.image(f"data:image/png;base64,{change_data['diff_image']}")
                        else:
                            if 'before' in change_data or 'after' in change_data:
                                diff_viz.visualize_diff(
                                    change_data.get('before', ''),
                                    change_data.get('after', '')
                                )
                        st.divider()

        with tab2:
            # Comparison view with interactive selection
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

                    # Create a unique diff visualizer for the comparison view
                    comparison_diff = DiffVisualizer(key_prefix=f"timeline_comparison_{timestamp1.strftime('%Y%m%d%H%M%S')}_{timestamp2.strftime('%Y%m%d%H%M%S')}")

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