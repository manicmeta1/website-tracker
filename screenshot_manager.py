import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from PIL import Image, ImageDraw
import io
from datetime import datetime, timedelta
import base64

class ScreenshotManager:
    def __init__(self):
        self.screenshot_dir = "screenshots"
        self._ensure_screenshot_dir()
        self._cleanup_old_screenshots()

    def _ensure_screenshot_dir(self):
        """Create screenshots directory if it doesn't exist"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
        # Ensure .gitkeep exists
        gitkeep_path = os.path.join(self.screenshot_dir, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, "w") as f:
                f.write("")

    def _cleanup_old_screenshots(self, max_age_hours=24):
        """Remove screenshots older than max_age_hours"""
        now = datetime.now()
        for filename in os.listdir(self.screenshot_dir):
            if filename == '.gitkeep':
                continue
            filepath = os.path.join(self.screenshot_dir, filename)
            file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            if now - file_modified > timedelta(hours=max_age_hours):
                try:
                    os.remove(filepath)
                except OSError as e:
                    print(f"Error removing old screenshot {filepath}: {e}")

    def capture_screenshot(self, url: str) -> str:
        """Capture website screenshot using Selenium"""
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")

            # Initialize Chrome webdriver
            driver = webdriver.Chrome(options=chrome_options)

            print(f"Navigating to URL: {url}")
            driver.get(url)
            driver.implicitly_wait(5)  # Wait for page to load

            print("Capturing screenshot...")
            screenshot = driver.get_screenshot_as_png()

            # Save screenshot with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(
                self.screenshot_dir,
                f"{url.replace('://', '_').replace('/', '_')}_{timestamp}.png"
            )

            print(f"Saving screenshot to: {filename}")
            with open(filename, "wb") as f:
                f.write(screenshot)

            driver.quit()
            return filename

        except Exception as e:
            print(f"Error capturing screenshot: {str(e)}")
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