from diff_match_patch import diff_match_patch
import streamlit as st
import html
from typing import Tuple, List

class DiffVisualizer:
    def __init__(self):
        self.dmp = diff_match_patch()

    def create_inline_diff(self, text1: str, text2: str) -> str:
        """
        Creates an inline diff visualization with word-level highlighting
        """
        diffs = self.dmp.diff_main(text1, text2)
        self.dmp.diff_cleanupSemantic(diffs)

        html_parts = []
        for op, text in diffs:
            text = html.escape(text)
            if op == 0:  # Equal
                html_parts.append(text)
            elif op == -1:  # Deletion
                html_parts.append(f'<span style="background-color: #ffb3b3; text-decoration: line-through;">{text}</span>')
            elif op == 1:  # Insertion
                html_parts.append(f'<span style="background-color: #b3ffb3; font-weight: bold;">{text}</span>')

        return ''.join(html_parts)

    def visualize_diff(self, before: str, after: str):
        """
        Display the diff visualization in Streamlit
        """
        st.markdown("### Change Details")

        # Create inline diff
        inline_diff = self.create_inline_diff(before, after)

        # Display diff with proper styling
        st.markdown(
            f'<div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; '
            f'margin: 10px 0; background-color: white; font-family: monospace; '
            f'line-height: 1.5; white-space: pre-wrap;">'
            f'<div style="margin-bottom: 10px; color: #666;">'
            f'<span style="background-color: #ffb3b3;">Removed</span> | '
            f'<span style="background-color: #b3ffb3;">Added</span>'
            f'</div>'
            f'{inline_diff}</div>',
            unsafe_allow_html=True
        )

    def get_diff_stats(self, before: str, after: str) -> dict:
        """
        Calculate statistics about the changes
        """
        diffs = self.dmp.diff_main(before, after)
        self.dmp.diff_cleanupSemantic(diffs)

        # Count words instead of characters
        def count_words(text: str) -> int:
            return len(text.split())

        stats = {
            'words_added': sum(count_words(text) for op, text in diffs if op == 1),
            'words_removed': sum(count_words(text) for op, text in diffs if op == -1),
            'total_changes': len([d for d in diffs if d[0] != 0])
        }

        return stats