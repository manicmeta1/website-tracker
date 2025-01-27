import streamlit as st
from screenshot_manager import ScreenshotManager
import os
import base64
from PIL import Image, ImageDraw
import io

# Initialize screenshot manager
screenshot_manager = ScreenshotManager()

# Main title
st.title("Screenshot Comparison Demo")

# Simple description
st.write("""
This demo shows how the screenshot comparison feature works by comparing two simple images.
""")

# Debug message
st.write("Debug: Main interface loaded")

# Create a clear separation
st.markdown("---")

# Sample comparison section
st.header("Sample Comparison")
st.write("Click the button below to generate and compare two sample images.")

# Debug message
st.write("Debug: About to render button")

# Simple button for sample comparison
if st.button("Generate Sample Comparison", key="sample_button"):
    st.write("Debug: Button clicked")

    try:
        # Create sample images for demonstration
        img1 = Image.new('RGB', (400, 300), 'white')
        draw1 = ImageDraw.Draw(img1)
        draw1.text((100, 150), "Original Content", fill="black")

        img2 = Image.new('RGB', (400, 300), 'white')
        draw2 = ImageDraw.Draw(img2)
        draw2.text((100, 150), "Updated Content", fill="blue")

        # Save temporary files
        img1.save("temp_before.png")
        img2.save("temp_after.png")

        st.write("Debug: Images created")

        # Compare screenshots
        before_img, after_img, diff_img = screenshot_manager.compare_screenshots(
            "temp_before.png",
            "temp_after.png"
        )

        st.write("Debug: Comparison completed")

        # Display results
        st.write("### Comparison Results")

        # Show images in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Before:**")
            st.image(f"data:image/png;base64,{before_img}", use_column_width=True)

        with col2:
            st.write("**After:**")
            st.image(f"data:image/png;base64,{after_img}", use_column_width=True)

        with col3:
            st.write("**Differences:**")
            st.image(f"data:image/png;base64,{diff_img}", use_column_width=True)

        # Cleanup
        os.remove("temp_before.png")
        os.remove("temp_after.png")

    except Exception as e:
        st.error(f"Error in sample comparison: {str(e)}")
        st.write(f"Debug: Error occurred - {str(e)}")

# Add an explanation
st.markdown("---")
st.write("""
### How it works:
1. Two sample images are generated with different text
2. The images are compared pixel by pixel
3. Differences are highlighted in red
4. Results show the before, after, and difference views
""")