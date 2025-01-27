import streamlit as st
from diff_visualizer import DiffVisualizer

# Initialize the diff visualizer
diff_visualizer = DiffVisualizer()

st.title("Diff Visualization Demo")

# Sample text content to demonstrate changes
before_text = """Welcome to Edica Naturals
We offer the finest natural skincare products.
Our products are made with organic ingredients.
Visit our store at 123 Nature Street.
Contact us for more information."""

after_text = """Welcome to Edica Naturals - Your Natural Beauty Partner
We offer the finest natural and organic skincare products.
Our products are made with premium organic ingredients sourced globally.
Visit our new store at 456 Wellness Avenue.
Contact us today to learn more about our products."""

# Display change statistics
stats = diff_visualizer.get_diff_stats(before_text, after_text)
st.write("### Change Statistics")
stat_cols = st.columns(3)
with stat_cols[0]:
    st.metric("Words Added", stats['words_added'])
with stat_cols[1]:
    st.metric("Words Removed", stats['words_removed'])
with stat_cols[2]:
    st.metric("Total Changes", stats['total_changes'])

# Show the diff visualization
st.write("### Text Changes")
diff_visualizer.visualize_diff(before_text, after_text)
