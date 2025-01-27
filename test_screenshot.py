import streamlit as st
from screenshot_manager import ScreenshotManager
import os
import base64
from PIL import Image, ImageDraw
import io

# Initialize screenshot manager
screenshot_manager = ScreenshotManager()

# Page title with custom styling
st.markdown("""
    <h1 style='text-align: center; padding: 20px 0;'>Screenshot Comparison Demo</h1>
""", unsafe_allow_html=True)

# Center-align description
st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        This demo shows how the screenshot comparison feature works by comparing two simple images.
        The button is located directly below this text.
    </div>
""", unsafe_allow_html=True)

# Add visual separation
st.markdown("<hr>", unsafe_allow_html=True)

# Center the button with custom styling
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #FF4B4B;
        color: white;
        font-size: 24px;
        padding: 20px 40px;
        display: block;
        margin: 40px auto;
        border-radius: 10px;
        border: none;
        width: 80%;
        max-width: 500px;
    }
    </style>
""", unsafe_allow_html=True)

# Large, centered button
if st.button("▶️ Run Comparison Demo"):
    try:
        st.info("Creating sample images for comparison...")

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

        # Compare screenshots
        before_img, after_img, diff_img = screenshot_manager.compare_screenshots(
            "temp_before.png",
            "temp_after.png"
        )

        # Display results
        st.markdown("<h2 style='text-align: center; padding: 20px 0;'>Comparison Results</h2>", unsafe_allow_html=True)

        # Show images in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("<p style='text-align: center'><b>Before:</b></p>", unsafe_allow_html=True)
            st.image(f"data:image/png;base64,{before_img}", use_column_width=True)

        with col2:
            st.markdown("<p style='text-align: center'><b>After:</b></p>", unsafe_allow_html=True)
            st.image(f"data:image/png;base64,{after_img}", use_column_width=True)

        with col3:
            st.markdown("<p style='text-align: center'><b>Differences:</b></p>", unsafe_allow_html=True)
            st.image(f"data:image/png;base64,{diff_img}", use_column_width=True)

        # Cleanup
        os.remove("temp_before.png")
        os.remove("temp_after.png")

    except Exception as e:
        st.error(f"Error in comparison: {str(e)}")
else:
    # Show instruction when button is not clicked
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            👆 Click the red button above to see the screenshot comparison demo in action!
        </div>
    """, unsafe_allow_html=True)

# Add explanation at the bottom
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h3>How it works:</h3>
        <ol style='display: inline-block; text-align: left;'>
            <li>Two sample images are generated with different text</li>
            <li>The images are compared pixel by pixel</li>
            <li>Differences are highlighted in red</li>
            <li>Results show before, after, and difference views</li>
        </ol>
    </div>
""", unsafe_allow_html=True)