import streamlit as st
from screenshot_manager import ScreenshotManager
from PIL import Image, ImageDraw
import os

# Initialize screenshot manager
screenshot_manager = ScreenshotManager()

# Basic page config
st.set_page_config(
    page_title="Screenshot Demo", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Create container for main content
main = st.container()

with main:
    st.title("📸 Screenshot Demo")
    st.markdown("### Click the button below to see a sample comparison")

    # Add a prominent button
    if st.button("Generate Sample Comparison", type="primary", use_container_width=True):
        try:
            # Create sample images
            with st.spinner("Generating comparison..."):
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
                cols = st.columns(3)

                with cols[0]:
                    st.subheader("Before")
                    st.image(f"data:image/png;base64,{before_img}")

                with cols[1]:
                    st.subheader("After")
                    st.image(f"data:image/png;base64,{after_img}")

                with cols[2]:
                    st.subheader("Differences")
                    st.image(f"data:image/png;base64,{diff_img}")

                # Cleanup temporary files
                os.remove("temp_before.png")
                os.remove("temp_after.png")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")