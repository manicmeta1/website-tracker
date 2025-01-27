import streamlit as st
from screenshot_manager import ScreenshotManager
import os

st.title("Screenshot Comparison Demo")

# Initialize screenshot manager
screenshot_manager = ScreenshotManager()

# Demo URLs - using real websites for demonstration
demo_urls = [
    "https://example.com",
    "https://httpbin.org/html"
]

# Add description
st.write("""
This demo shows how the screenshot comparison feature works. 
It will capture screenshots of two different websites and show the visual differences between them.
""")

if st.button("Run Screenshot Comparison Demo"):
    with st.spinner("Capturing and comparing screenshots..."):
        try:
            # Capture screenshots
            screenshot1 = screenshot_manager.capture_screenshot(demo_urls[0])
            st.success(f"Captured first screenshot: {os.path.basename(screenshot1)}")
            
            screenshot2 = screenshot_manager.capture_screenshot(demo_urls[1])
            st.success(f"Captured second screenshot: {os.path.basename(screenshot2)}")
            
            # Compare screenshots
            before_img, after_img, diff_img = screenshot_manager.compare_screenshots(
                screenshot1, 
                screenshot2
            )
            
            # Display results
            st.write("### Screenshot Comparison Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("Before (example.com)")
                st.image(f"data:image/png;base64,{before_img}")
                
            with col2:
                st.write("After (httpbin.org)")
                st.image(f"data:image/png;base64,{after_img}")
                
            with col3:
                st.write("Differences (in red)")
                st.image(f"data:image/png;base64,{diff_img}")
                
        except Exception as e:
            st.error(f"Error during demo: {str(e)}")
