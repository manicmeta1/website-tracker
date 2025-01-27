from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw
import os
from datetime import datetime
import io
import base64

class ScreenshotManager:
    def __init__(self):
        self.screenshot_dir = "screenshots"
        self._ensure_screenshot_dir()

    def _ensure_screenshot_dir(self):
        """Create screenshots directory if it doesn't exist"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def capture_screenshot(self, url: str) -> str:
        """Capture website screenshot using Selenium"""
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")  # Required for headless on some systems
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.binary_location = "/nix/store/zi4f80l169xlmivz8vwlphq74qqk0-chromium-125.0.6422.141/bin/chromium-browser"

            # Initialize WebDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Capture screenshot
            driver.get(url)
            driver.implicitly_wait(5)  # Wait for page to load
            screenshot = driver.get_screenshot_as_png()

            # Save screenshot with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.screenshot_dir}/{url.replace('://', '_').replace('/', '_')}_{timestamp}.png"

            with open(filename, "wb") as f:
                f.write(screenshot)

            driver.quit()
            return filename

        except Exception as e:
            raise Exception(f"Failed to capture screenshot: {str(e)}")

    def compare_screenshots(self, before_path: str, after_path: str) -> tuple:
        """Compare two screenshots and highlight differences"""
        try:
            # Open images
            before_img = Image.open(before_path)
            after_img = Image.open(after_path)

            # Ensure same size
            size = (1920, 1080)  # Standard size
            before_img = before_img.resize(size)
            after_img = after_img.resize(size)

            # Convert to RGB
            before_img = before_img.convert('RGB')
            after_img = after_img.convert('RGB')

            # Create diff image
            diff_img = Image.new('RGB', size)
            draw = ImageDraw.Draw(diff_img)

            # Compare pixels
            for x in range(size[0]):
                for y in range(size[1]):
                    before_pixel = before_img.getpixel((x, y))
                    after_pixel = after_img.getpixel((x, y))

                    if before_pixel != after_pixel:
                        # Highlight difference in red
                        draw.point((x, y), fill='red')
                    else:
                        # Keep original pixel
                        diff_img.putpixel((x, y), after_pixel)

            # Convert images to base64 for display
            def img_to_base64(img):
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                return base64.b64encode(buffered.getvalue()).decode()

            return (
                img_to_base64(before_img),
                img_to_base64(after_img),
                img_to_base64(diff_img)
            )

        except Exception as e:
            raise Exception(f"Failed to compare screenshots: {str(e)}")