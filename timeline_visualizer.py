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

        # Timeline header with controls
        st.markdown("### 📅 Website Changes Timeline")

        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Timeline View", "Comparison View", "Analytics View"])

        with tab1:
            # Date range selector
            col1, col2 = st.columns(2)
            with col1:
                min_date = df['timestamp'].min().date()
                max_date = df['timestamp'].max().date()
                start_date = st.date_input(
                    "Start Date",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="timeline_start_date"
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="timeline_end_date"
                )

            # Advanced filters
            with st.expander("📊 Advanced Filters", expanded=True):
                filter_cols = st.columns([1, 1, 1, 1])

                with filter_cols[0]:
                    selected_url = st.selectbox(
                        "Website",
                        options=['All'] + list(df['url'].unique()),
                        key="timeline_url_filter"
                    )

                with filter_cols[1]:
                    selected_type = st.selectbox(
                        "Change Type",
                        options=['All'] + list(df['type'].unique()),
                        key="timeline_type_filter"
                    )

                with filter_cols[2]:
                    min_significance = st.slider(
                        "Min Significance",
                        min_value=1,
                        max_value=10,
                        value=1,
                        key="significance_filter"
                    )

                with filter_cols[3]:
                    sort_order = st.selectbox(
                        "Sort By",
                        options=['Newest First', 'Oldest First', 'Significance'],
                        key="timeline_sort"
                    )

            # Apply filters
            filtered_df = df.copy()
            filtered_df = filtered_df[
                (filtered_df['timestamp'].dt.date >= start_date) &
                (filtered_df['timestamp'].dt.date <= end_date)
            ]

            if selected_url != 'All':
                filtered_df = filtered_df[filtered_df['url'] == selected_url]
            if selected_type != 'All':
                filtered_df = filtered_df[filtered_df['type'] == selected_type]

            filtered_df = filtered_df[
                filtered_df['significance'] >= min_significance
            ]

            # Sort the data
            if sort_order == 'Newest First':
                filtered_df = filtered_df.sort_values('timestamp', ascending=False)
            elif sort_order == 'Oldest First':
                filtered_df = filtered_df.sort_values('timestamp')
            else:  # Sort by significance
                filtered_df = filtered_df.sort_values('significance', ascending=False)

            # Display timeline statistics
            st.markdown("#### Timeline Overview")
            stat_cols = st.columns(4)
            with stat_cols[0]:
                st.metric("Total Changes", len(filtered_df))
            with stat_cols[1]:
                avg_significance = filtered_df['significance'].mean()
                st.metric("Avg Significance", f"{avg_significance:.1f}")
            with stat_cols[2]:
                st.metric("Time Range", f"{(end_date - start_date).days + 1} days")
            with stat_cols[3]:
                st.metric("Unique Websites", len(filtered_df['url'].unique()))

            # Interactive timeline visualization
            st.markdown("#### Changes Timeline")

            # Create timeline chart
            timeline_chart_data = filtered_df.copy()
            timeline_chart_data['date'] = timeline_chart_data['timestamp'].dt.date
            timeline_chart_data['count'] = 1
            daily_changes = timeline_chart_data.groupby('date')['count'].sum().reset_index()
            st.line_chart(daily_changes.set_index('date'))

            # Display changes in an interactive list
            for idx, change in filtered_df.iterrows():
                change_data = change['change_data']
                significance_score = change_data.get('significance_score', 0)
                analysis = change_data.get('analysis', {})

                # Create expandable card for each change
                with st.expander(
                    f"{self._get_change_icon(change['type'])} "
                    f"{change['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - "
                    f"{change['type'].replace('_', ' ').title()} "
                    f"(Significance: {significance_score}/10)",
                    expanded=False
                ):
                    # Change details
                    st.markdown(f"""
                    <div style='border:1px solid #ddd; border-radius:5px; padding:10px; margin:5px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <h4>{change['type'].replace('_', ' ').title()}</h4>
                            <span style='background-color: {"#28a745" if significance_score >= 7 else "#ffc107" if significance_score >= 4 else "#dc3545"}; 
                                       color: white; padding: 5px 10px; border-radius: 15px;'>
                                Significance: {significance_score}/10
                            </span>
                        </div>
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
                            st.markdown("##### Content Changes")
                            diff_viz = DiffVisualizer(key_prefix=f"timeline_{idx}")
                            diff_viz.visualize_diff(
                                change_data.get('before', ''),
                                change_data.get('after', '')
                            )

        with tab2:
            self._render_comparison_view(filtered_df)

        with tab3:
            self._render_analytics_view(filtered_df)

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