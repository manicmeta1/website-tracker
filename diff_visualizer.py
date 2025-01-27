from diff_match_patch import diff_match_patch
import streamlit as st
import html
from typing import Tuple, List

class DiffVisualizer:
    def __init__(self):
        self.dmp = diff_match_patch()
        
    def create_diff_html(self, text1: str, text2: str) -> Tuple[str, str]:
        """
        Creates HTML for side-by-side diff visualization with highlighting
        """
        # Compute diffs
        diffs = self.dmp.diff_main(text1, text2)
        self.dmp.diff_cleanupSemantic(diffs)
        
        # Generate HTML for both sides
        left_html = []
        right_html = []
        
        for op, text in diffs:
            text = html.escape(text)
            
            if op == 0:  # Equal
                left_html.append(f'<span style="color: #666">{text}</span>')
                right_html.append(f'<span style="color: #666">{text}</span>')
            elif op == -1:  # Deletion
                left_html.append(f'<span style="background-color: #ffd7d7">{text}</span>')
            elif op == 1:  # Insertion
                right_html.append(f'<span style="background-color: #d7ffd7">{text}</span>')
                
        return ''.join(left_html), ''.join(right_html)
    
    def visualize_diff(self, before: str, after: str):
        """
        Display the diff visualization in Streamlit
        """
        # Create diff HTML
        left_html, right_html = self.create_diff_html(before, after)
        
        # Create columns for side-by-side display
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Before")
            st.markdown(
                f'<div style="border: 1px solid #ddd; padding: 10px; '
                f'background-color: white; font-family: monospace; '
                f'white-space: pre-wrap;">{left_html}</div>',
                unsafe_allow_html=True
            )
            
        with col2:
            st.markdown("### After")
            st.markdown(
                f'<div style="border: 1px solid #ddd; padding: 10px; '
                f'background-color: white; font-family: monospace; '
                f'white-space: pre-wrap;">{right_html}</div>',
                unsafe_allow_html=True
            )
            
    def get_diff_stats(self, before: str, after: str) -> dict:
        """
        Calculate statistics about the changes
        """
        diffs = self.dmp.diff_main(before, after)
        self.dmp.diff_cleanupSemantic(diffs)
        
        stats = {
            'chars_added': sum(len(text) for op, text in diffs if op == 1),
            'chars_removed': sum(len(text) for op, text in diffs if op == -1),
            'total_changes': len([d for d in diffs if d[0] != 0])
        }
        
        return stats
