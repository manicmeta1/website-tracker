import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
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

    def _hex_to_rgba(self, hex_color: str, alpha: float = 0.1) -> str:
        """Convert hex color to rgba format"""
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        # Convert hex to RGB values
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'rgba({r}, {g}, {b}, {alpha})'

    def visualize_timeline(self, changes: List[Dict[str, Any]]):
        """Create an interactive timeline visualization of changes"""
        if not changes:
            st.info("No changes to display in the timeline.")
            return

        # Display significance legend
        self._show_significance_legend()

        # Group changes by URL
        changes_by_url = {}
        for change in changes:
            url = change.get('url', 'Unknown')
            if url not in changes_by_url:
                changes_by_url[url] = []
            changes_by_url[url].append(change)

        # Display changes for each URL
        for url, url_changes in changes_by_url.items():
            st.markdown(f"### 🌐 {url}")

            # Sort changes by timestamp in reverse order
            sorted_changes = sorted(url_changes, key=lambda x: x['timestamp'], reverse=True)

            for change in sorted_changes:
                score = change.get('significance_score', 5)
                color = self._get_significance_color(score)
                bg_color = self._hex_to_rgba(color)

                # Create the main change card
                st.markdown(
                    f'<div style="border-left: 5px solid {color}; padding: 10px; margin: 10px 0; '
                    f'background-color: {bg_color};">'
                    f'<h4>{change["type"].replace("_", " ").title()}</h4>'
                    f'<p><strong>Time:</strong> {change["timestamp"]}</p>'
                    f'<p><strong>Location:</strong> {change["location"]}</p>'
                    f'<p><strong>Significance:</strong> {score} ({self._get_significance_label(score)})</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Show analysis in columns
                if 'analysis' in change:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Impact Analysis**")
                        st.write(f"- Category: {change['analysis'].get('impact_category', 'Unknown')}")
                        st.write(f"- Business Relevance: {change['analysis'].get('business_relevance', 'Unknown')}")
                    with col2:
                        st.markdown("**Recommendations**")
                        st.write(f"- {change['analysis'].get('recommendations', 'No recommendations available')}")
                        st.write(f"- {change['analysis'].get('explanation', 'No explanation available')}")

                # Show content changes
                if 'before' in change and 'after' in change:
                    st.markdown("**Content Changes**")
                    self.diff_visualizer.visualize_diff(
                        change['before'],
                        change['after'],
                        f"change_{change['timestamp']}"
                    )

                st.markdown("---")  # Add separator between changes

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