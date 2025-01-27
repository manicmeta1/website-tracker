import streamlit as st
from screenshot_manager import ScreenshotManager
import os
import base64
from PIL import Image, ImageDraw
import io
import sys

# Configure port and error handling
if __name__ == "__main__":
    try:
        st.set_page_config(
            page_title="Screenshot Comparison Demo",
            page_icon="📸",
            layout="wide"
        )

        # Initialize screenshot manager
        screenshot_manager = ScreenshotManager()

        # Page title with custom styling
        st.title("📸 Screenshot Comparison Demo")

        # Clear description
        st.markdown("""
        ### Instructions:
        Click the big red button below to see how the screenshot comparison works!
        """)

        # Make the button very prominent
        st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #FF4B4B;
            color: white;
            font-size: 28px;
            padding: 25px 50px;
            display: block;
            margin: 50px auto;
            border-radius: 15px;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 600px;
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.2);
        }
        </style>
        """, unsafe_allow_html=True)

        # Demo button
        if st.button("🎯 CLICK HERE TO RUN DEMO", key="demo_button"):
            with st.spinner("Generating comparison images..."):
                try:
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

                    try:
                        # Compare screenshots
                        before_img, after_img, diff_img = screenshot_manager.compare_screenshots(
                            "temp_before.png",
                            "temp_after.png"
                        )

                        # Show results
                        st.success("Comparison completed successfully!")

                        st.markdown("### 👀 Comparison Results")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown("**Before:**")
                            st.image(f"data:image/png;base64,{before_img}")

                        with col2:
                            st.markdown("**After:**")
                            st.image(f"data:image/png;base64,{after_img}")

                        with col3:
                            st.markdown("**Changes:**")
                            st.image(f"data:image/png;base64,{diff_img}")

                    except Exception as e:
                        st.error(f"Error during comparison: {str(e)}")
                        st.info("Please try again. If the error persists, contact support.")

                    # Cleanup temporary files
                    if os.path.exists("temp_before.png"):
                        os.remove("temp_before.png")
                    if os.path.exists("temp_after.png"):
                        os.remove("temp_after.png")

                except Exception as e:
                    st.error(f"Error creating sample images: {str(e)}")
                    st.info("Please try again. If the error persists, contact support.")

        else:
            # Show prominent call-to-action when button is not clicked
            st.markdown("""
                <div style='text-align: center; margin: 50px 0; padding: 30px; background-color: #f0f2f6; border-radius: 10px;'>
                    <h2>👆 Click the red button above!</h2>
                    <p style='font-size: 18px;'>See how we detect and highlight changes between images</p>
                </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please refresh the page. If the error persists, contact support.")