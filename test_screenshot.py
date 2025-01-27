import streamlit as st
from screenshot_manager import ScreenshotManager
from PIL import Image, ImageDraw
import os

# Initialize screenshot manager
screenshot_manager = ScreenshotManager()

# Configure page with custom theme
st.set_page_config(
    page_title="Screenshot Demo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to make button more prominent
st.markdown("""
<style>
    .stButton>button {
        background-color: #FF4B4B !important;
        color: white !important;
        font-size: 20px !important;
        height: 60px !important;
        width: 100% !important;
        margin-top: 30px !important;
        margin-bottom: 30px !important;
    }
    .big-text {
        font-size: 24px !important;
        margin-bottom: 30px !important;
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.title("📸 Screenshot Comparison Demo")
st.markdown('<p class="big-text">Press the big red button below to see the demo!</p>', unsafe_allow_html=True)

# Prominent button spanning full width
if st.button("▶️ CLICK HERE TO GENERATE SAMPLE COMPARISON", use_container_width=True):
    try:
        with st.spinner("Creating comparison..."):
            # Create sample images
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

            # Display results in columns
            st.success("Comparison generated successfully!")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### Before")
                st.image(f"data:image/png;base64,{before_img}")

            with col2:
                st.markdown("### After")
                st.image(f"data:image/png;base64,{after_img}")

            with col3:
                st.markdown("### Differences")
                st.image(f"data:image/png;base64,{diff_img}")

            # Cleanup temporary files
            os.remove("temp_before.png")
            os.remove("temp_after.png")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    # Show prominent message when button is not clicked
    st.info("👆 Click the red button above to see how we detect changes between images!")