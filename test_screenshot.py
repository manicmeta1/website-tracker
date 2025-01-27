import streamlit as st
from screenshot_manager import ScreenshotManager
import os
import base64
from PIL import Image
import io

st.title("Screenshot Comparison Demo")

# Initialize screenshot manager
screenshot_manager = ScreenshotManager()

# Create two columns for the main layout
left_col, right_col = st.columns([2, 1])

with left_col:
    # Add description
    st.write("""
    This demo shows how the screenshot comparison feature works. 
    It will capture screenshots of two different websites and show the visual differences between them.

    The comparison highlights changes in:
    - Layout
    - Content
    - Images
    - Text
    """)

# Create tabs for different demo options
tab1, tab2 = st.tabs(["Live Website Comparison", "Sample Demo"])

with tab1:
    st.header("Compare Two Websites")
    # Demo URLs - using real websites for demonstration
    url1 = st.text_input("First Website URL", value="https://example.com")
    url2 = st.text_input("Second Website URL", value="https://httpbin.org/html")

    if st.button("Compare Websites", key="compare_live"):
        with st.spinner("Capturing and comparing screenshots..."):
            try:
                # Capture screenshots
                screenshot1 = screenshot_manager.capture_screenshot(url1)
                st.success(f"✅ Captured first screenshot")

                screenshot2 = screenshot_manager.capture_screenshot(url2)
                st.success(f"✅ Captured second screenshot")

                # Compare screenshots
                before_img, after_img, diff_img = screenshot_manager.compare_screenshots(
                    screenshot1, 
                    screenshot2
                )

                # Display results
                st.write("### Comparison Results")

                # Show stats about the differences
                st.write("📊 **Difference Overview**")
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Before Screenshot Size", "1920x1080")
                with cols[1]:
                    st.metric("After Screenshot Size", "1920x1080")
                with cols[2]:
                    st.metric("Comparison Method", "Pixel-level")

                # Display the images
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**Before:**")
                    st.image(f"data:image/png;base64,{before_img}", use_column_width=True)

                with col2:
                    st.write("**After:**")
                    st.image(f"data:image/png;base64,{after_img}", use_column_width=True)

                with col3:
                    st.write("**Differences (in red):**")
                    st.image(f"data:image/png;base64,{diff_img}", use_column_width=True)

            except Exception as e:
                st.error(f"Error during comparison: {str(e)}")
                st.info("Please try the Sample Demo tab to see how the feature works.")

with tab2:
    st.header("Sample Visual Comparison")
    st.write("""
    This demo shows how the comparison feature works using sample images, 
    without needing to capture live websites.
    """)

    # Add a prominent button for sample comparison
    if st.button("▶️ Run Sample Comparison Demo", type="primary", key="sample_demo"):
        try:
            # Create sample images for demonstration
            def create_sample_image(text, color):
                img = Image.new('RGB', (400, 300), 'white')
                draw = ImageDraw.Draw(img)
                draw.text((100, 150), text, fill=color)
                return img

            # Create sample images
            img1 = create_sample_image("Original Content", "black")
            img2 = create_sample_image("Updated Content", "blue")

            # Save temporary files for comparison
            img1.save("temp_before.png")
            img2.save("temp_after.png")

            # Compare screenshots
            before_img, after_img, diff_img = screenshot_manager.compare_screenshots(
                "temp_before.png",
                "temp_after.png"
            )

            # Display results
            st.write("### Sample Comparison Results")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Before:**")
                st.image(f"data:image/png;base64,{before_img}", use_column_width=True)

            with col2:
                st.write("**After:**")
                st.image(f"data:image/png;base64,{after_img}", use_column_width=True)

            with col3:
                st.write("**Differences (in red):**")
                st.image(f"data:image/png;base64,{diff_img}", use_column_width=True)

            # Cleanup temporary files
            os.remove("temp_before.png")
            os.remove("temp_after.png")

        except Exception as e:
            st.error(f"Error in sample comparison: {str(e)}")

# How it works section at the bottom
st.write("---")
st.write("""
### How it works
1. Screenshots are captured using Selenium WebDriver
2. Images are processed using Pillow (PIL)
3. Pixel-by-pixel comparison highlights differences
4. Changes are marked in red in the difference view
""")