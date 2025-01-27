from diff_match_patch import diff_match_patch
import streamlit as st
import html
from typing import Tuple, List, Optional, Dict
import base64
from io import BytesIO

class DiffVisualizer:
    def __init__(self):
        self.dmp = diff_match_patch()
        self.color_schemes = {
            "Default": {
                "deletion": "#ffb3b3",
                "insertion": "#b3ffb3",
                "unchanged": "#ffffff"
            },
            "Dark": {
                "deletion": "#ff4d4d",
                "insertion": "#4dff4d",
                "unchanged": "#2b2b2b"
            },
            "Pastel": {
                "deletion": "#ffd6d6",
                "insertion": "#d6ffd6",
                "unchanged": "#f8f9fa"
            }
        }
        self.current_scheme = "Default"

    def _create_diff(self, text1: str, text2: str, char_level: bool = False) -> List[Tuple[int, str]]:
        """Creates diff with option for character or word level comparison"""
        if char_level:
            return self.dmp.diff_main(text1, text2)

        # Word level diff
        words1 = text1.split()
        words2 = text2.split()
        return self.dmp.diff_main(" ".join(words1), " ".join(words2))

    def create_side_by_side_diff(self, text1: str, text2: str, char_level: bool = False) -> Tuple[str, str]:
        """Creates side-by-side diff visualization"""
        diffs = self._create_diff(text1, text2, char_level)
        self.dmp.diff_cleanupSemantic(diffs)

        left_html = []
        right_html = []
        colors = self.color_schemes[self.current_scheme]

        for op, text in diffs:
            text = html.escape(text)
            if op == 0:  # Equal
                left_html.append(f'<span style="background-color: {colors["unchanged"]}">{text}</span>')
                right_html.append(f'<span style="background-color: {colors["unchanged"]}">{text}</span>')
            elif op == -1:  # Deletion
                left_html.append(f'<span style="background-color: {colors["deletion"]}; text-decoration: line-through;">{text}</span>')
            elif op == 1:  # Insertion
                right_html.append(f'<span style="background-color: {colors["insertion"]}; font-weight: bold;">{text}</span>')

        return ''.join(left_html), ''.join(right_html)

    def create_inline_diff(self, text1: str, text2: str, char_level: bool = False) -> str:
        """Creates an inline diff visualization"""
        diffs = self._create_diff(text1, text2, char_level)
        self.dmp.diff_cleanupSemantic(diffs)

        html_parts = []
        colors = self.color_schemes[self.current_scheme]

        for op, text in diffs:
            text = html.escape(text)
            if op == 0:  # Equal
                html_parts.append(text)
            elif op == -1:  # Deletion
                html_parts.append(f'<span style="background-color: {colors["deletion"]}; text-decoration: line-through;">{text}</span>')
            elif op == 1:  # Insertion
                html_parts.append(f'<span style="background-color: {colors["insertion"]}; font-weight: bold;">{text}</span>')

        return ''.join(html_parts)

    def get_diff_stats(self, before: str, after: str) -> dict:
        """Calculate statistics about the changes"""
        diffs = self.dmp.diff_main(before, after)
        self.dmp.diff_cleanupSemantic(diffs)

        def count_words(text: str) -> int:
            return len(text.split())

        stats = {
            'words_added': sum(count_words(text) for op, text in diffs if op == 1),
            'words_removed': sum(count_words(text) for op, text in diffs if op == -1),
            'total_changes': len([d for d in diffs if d[0] != 0])
        }

        return stats

    def export_diff_html(self, before: str, after: str, char_level: bool = False) -> str:
        """Export the diff as standalone HTML"""
        if st.session_state.get('diff_view_mode') == 'side-by-side':
            left_diff, right_diff = self.create_side_by_side_diff(before, after, char_level)
            html_content = f"""
            <html>
            <head>
                <style>
                    .diff-container {{ display: flex; justify-content: space-between; }}
                    .diff-side {{ width: 48%; padding: 10px; border: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="diff-container">
                    <div class="diff-side">
                        <h3>Before</h3>
                        {left_diff}
                    </div>
                    <div class="diff-side">
                        <h3>After</h3>
                        {right_diff}
                    </div>
                </div>
            </body>
            </html>
            """
        else:
            inline_diff = self.create_inline_diff(before, after, char_level)
            html_content = f"""
            <html>
            <head>
                <style>
                    .diff-container {{ padding: 20px; }}
                </style>
            </head>
            <body>
                <div class="diff-container">
                    {inline_diff}
                </div>
            </body>
            </html>
            """

        return html_content

    def visualize_diff(self, before: str, after: str):
        """Display the diff visualization in Streamlit with advanced options"""
        st.markdown("### Change Details")

        # Diff options section using columns instead of expander
        st.markdown("#### Visualization Options")
        col1, col2 = st.columns(2)

        with col1:
            # View mode selection
            view_mode = st.radio(
                "View Mode",
                ['inline', 'side-by-side'],
                key='diff_view_mode'
            )

            # Comparison level
            char_level = st.checkbox(
                "Character-level comparison",
                key='char_level_diff',
                help="Compare character by character instead of word by word"
            )

        with col2:
            # Color scheme selection
            self.current_scheme = st.selectbox(
                "Color Scheme",
                options=list(self.color_schemes.keys()),
                key='color_scheme'
            )

        # Calculate and display statistics
        stats = self.get_diff_stats(before, after)
        stat_cols = st.columns(3)
        with stat_cols[0]:
            st.metric("Words Added", stats['words_added'])
        with stat_cols[1]:
            st.metric("Words Removed", stats['words_removed'])
        with stat_cols[2]:
            st.metric("Total Changes", stats['total_changes'])

        # Display the diff based on selected view mode
        if view_mode == 'side-by-side':
            left_diff, right_diff = self.create_side_by_side_diff(before, after, char_level)
            cols = st.columns(2)
            with cols[0]:
                st.markdown("#### Before")
                st.markdown(
                    f'<div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px;">{left_diff}</div>',
                    unsafe_allow_html=True
                )
            with cols[1]:
                st.markdown("#### After")
                st.markdown(
                    f'<div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px;">{right_diff}</div>',
                    unsafe_allow_html=True
                )
        else:
            inline_diff = self.create_inline_diff(before, after, char_level)
            st.markdown(
                f'<div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; '
                f'margin: 10px 0; background-color: white; font-family: monospace; '
                f'line-height: 1.5; white-space: pre-wrap;">'
                f'<div style="margin-bottom: 10px; color: #666;">'
                f'<span style="background-color: {self.color_schemes[self.current_scheme]["deletion"]}">Removed</span> | '
                f'<span style="background-color: {self.color_schemes[self.current_scheme]["insertion"]}">Added</span>'
                f'</div>'
                f'{inline_diff}</div>',
                unsafe_allow_html=True
            )

        # Export options
        if st.button("Export as HTML"):
            html_content = self.export_diff_html(before, after, char_level)
            b64 = base64.b64encode(html_content.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="diff_export.html">Download HTML</a>'
            st.markdown(href, unsafe_allow_html=True)