import trafilatura
from bs4 import BeautifulSoup
import requests
from typing import Dict, Any, List, Set
from urllib.parse import urlparse, urljoin
import time
import random
import re # Added for regex in _extract_links
from screenshot_manager import ScreenshotManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        self.screenshot_manager = ScreenshotManager()
        self.visited_urls = set()
        self._logs = []
        self.session = requests.Session()
        self.retry_count = 3
        self.retry_delay = 2

        # Configure Chrome options for Replit environment
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.binary_location = "/nix/store/x205pbkd5xh5g4iv0g58xjla55has3cx-chromium-108.0.5359.94/bin/chromium"

        try:
            self._log("Initializing Chrome WebDriver...")
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self._log("Chrome WebDriver initialized successfully")
        except Exception as e:
            self._log(f"Failed to initialize Chrome WebDriver: {str(e)}")
            self.driver = None

    def __del__(self):
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except:
            pass

    def _log(self, message: str):
        """Add a log message with timestamp"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)  # Print to console for immediate feedback
        self._logs.append(log_entry)

    def _normalize_url(self, url: str) -> str:
        """Normalize URL and standardize domain format"""
        try:
            # Handle URLs without scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url.lstrip('/')

            parsed = urlparse(url)
            netloc = parsed.netloc.lower()

            # Remove www. if present
            if netloc.startswith('www.'):
                netloc = netloc[4:]

            # Keep query parameters for pagination but remove fragments
            query = parsed.query
            path = parsed.path
            if not path:
                path = '/'

            # Construct final URL
            final_url = f"https://{netloc}{path}"
            if query:
                final_url += f"?{query}"

            self._log(f"Normalized URL: {url} -> {final_url}")
            return final_url

        except Exception as e:
            self._log(f"Error normalizing URL {url}: {str(e)}")
            raise Exception(f"Invalid URL format: {url}")

    def _is_valid_internal_link(self, url: str, base_domain: str) -> bool:
        """Check if URL is a valid internal link"""
        try:
            if not url:
                return False

            parsed = urlparse(url)
            netloc = parsed.netloc.lower()
            if netloc.startswith('www.'):
                netloc = netloc[4:]

            base_domain = base_domain.lower()
            if base_domain.startswith('www.'):
                base_domain = base_domain[4:]

            # File extensions to exclude
            excluded_extensions = [
                '.jpg', '.jpeg', '.png', '.gif', '.css', '.js',
                '.ico', '.woff', '.woff2', '.pdf', '.zip'
            ]

            # Check if it's a valid internal URL
            is_valid = (
                (netloc == base_domain or not netloc) and
                not any(url.endswith(ext) for ext in excluded_extensions) and
                not url.endswith(base_domain)  # Avoid duplicate root URLs
            )

            if is_valid:
                self._log(f"Valid internal link found: {url}")
            return is_valid

        except Exception as e:
            self._log(f"Error validating URL {url}: {str(e)}")
            return False

    def _get_dynamic_content(self, url: str) -> str:
        """Get page content after JavaScript execution"""
        if not self.driver:
            self._log("WebDriver not initialized, skipping dynamic content")
            return None

        try:
            self._log(f"Loading dynamic content for {url}")
            self.driver.get(url)

            # Wait for dynamic content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Scroll multiple times to trigger lazy loading
            for _ in range(3):
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(1)

            return self.driver.page_source
        except Exception as e:
            self._log(f"Error getting dynamic content: {str(e)}")
            return None

    def _extract_links(self, soup: BeautifulSoup, base_url: str, base_domain: str) -> Set[str]:
        """Extract all valid internal links from the page"""
        links = set()
        self._log(f"Extracting links from {base_url}")

        # Find all <a> tags
        for a in soup.find_all('a', href=True):
            href = a.get('href', '').strip()
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
                try:
                    # Handle relative URLs
                    full_url = urljoin(base_url, href)
                    normalized_url = self._normalize_url(full_url)

                    if self._is_valid_internal_link(normalized_url, base_domain):
                        links.add(normalized_url)
                        self._log(f"Found valid link: {normalized_url}")
                except Exception as e:
                    self._log(f"Error processing link {href}: {str(e)}")

        # Find links in onclick attributes and data attributes
        for element in soup.find_all(attrs={'onclick': True}):
            onclick = element.get('onclick', '')
            urls = re.findall(r'window\.location\.href=[\'"]([^\'"]+)[\'"]', onclick)
            for url in urls:
                try:
                    full_url = urljoin(base_url, url)
                    normalized_url = self._normalize_url(full_url)
                    if self._is_valid_internal_link(normalized_url, base_domain):
                        links.add(normalized_url)
                        self._log(f"Found onclick link: {normalized_url}")
                except Exception as e:
                    self._log(f"Error processing onclick URL {url}: {str(e)}")

        self._log(f"Extracted {len(links)} valid internal links")
        return links

    def scrape_website(self, url: str, crawl_all_pages: bool = False) -> Dict[str, Any]:
        """Scrape website content with improved crawling logic"""
        try:
            self.clear_logs()
            self._log(f"Starting new crawl of {url}")
            self._log(f"Full site crawling: {'enabled' if crawl_all_pages else 'disabled'}")

            # Progress tracking variables
            self.total_discovered_pages = 0
            self.processed_pages = 0
            self.start_time = time.time()

            # Normalize initial URL
            url = self._normalize_url(url)
            base_domain = urlparse(url).netloc
            if base_domain.startswith('www.'):
                base_domain = base_domain[4:]
            self._log(f"Base domain: {base_domain}")

            # Reset visited URLs for new crawl
            self.visited_urls.clear()

            # Get initial page content
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            initial_content = response.text

            # Try to get dynamic content
            dynamic_content = self._get_dynamic_content(url)
            if dynamic_content:
                self._log("Using dynamic content from Selenium")
                html_content = dynamic_content
            else:
                self._log("Using static content from requests")
                html_content = initial_content

            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract text content
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text_content = trafilatura.extract(downloaded)
            else:
                text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])

            # Extract links
            links = self._extract_links(soup, url, base_domain)
            self.total_discovered_pages = len(links) + 1  # +1 for the initial page
            self._log(f"Found {len(links)} links on initial page")

            # Take screenshot
            screenshot_path = self.screenshot_manager.capture_screenshot(url)
            self.processed_pages += 1
            self._log(f"Processed {self.processed_pages}/{self.total_discovered_pages} pages")

            # Store initial page data
            pages_data = [{
                'url': url,
                'location': '/',
                'content': {
                    'url': url,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'text_content': text_content,
                    'links': list(links),
                    'content_hash': hash(text_content),
                    'screenshot_path': screenshot_path
                }
            }]

            if crawl_all_pages:
                urls_to_visit = links - self.visited_urls
                self._log(f"Found {len(urls_to_visit)} new pages to crawl")

                while urls_to_visit and len(self.visited_urls) < 100:
                    next_url = urls_to_visit.pop()
                    if next_url not in self.visited_urls:
                        elapsed_time = time.time() - self.start_time
                        avg_time_per_page = elapsed_time / self.processed_pages if self.processed_pages > 0 else 0
                        remaining_pages = self.total_discovered_pages - self.processed_pages
                        estimated_time = avg_time_per_page * remaining_pages

                        self._log(f"Progress: {self.processed_pages}/{self.total_discovered_pages} pages")
                        self._log(f"Estimated time remaining: {int(estimated_time)} seconds")
                        self._log(f"Crawling: {next_url}")

                        time.sleep(random.uniform(1, 2))  # Polite delay

                        try:
                            response = self.session.get(next_url, headers=self.headers, timeout=30)
                            response.raise_for_status()
                            html_content = response.text

                            # Try dynamic content
                            dynamic_content = self._get_dynamic_content(next_url)
                            if dynamic_content:
                                html_content = dynamic_content

                            soup = BeautifulSoup(html_content, 'html.parser')

                            # Extract text
                            downloaded = trafilatura.fetch_url(next_url)
                            if downloaded:
                                text_content = trafilatura.extract(downloaded)
                            else:
                                text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])

                            # Extract more links
                            new_links = self._extract_links(soup, next_url, base_domain)
                            new_unvisited_links = new_links - self.visited_urls
                            urls_to_visit.update(new_unvisited_links)

                            # Update total discovered pages
                            self.total_discovered_pages += len(new_unvisited_links)

                            # Take screenshot
                            screenshot_path = self.screenshot_manager.capture_screenshot(next_url)

                            # Add to visited pages
                            self.visited_urls.add(next_url)
                            parsed_url = urlparse(next_url)
                            location = parsed_url.path if parsed_url.path else '/'

                            pages_data.append({
                                'url': next_url,
                                'location': location,
                                'content': {
                                    'url': next_url,
                                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                                    'text_content': text_content,
                                    'links': list(new_links),
                                    'content_hash': hash(text_content),
                                    'screenshot_path': screenshot_path
                                }
                            })

                            self.processed_pages += 1
                            self._log(f"Successfully crawled {next_url}")
                            self._log(f"Found {len(new_links)} new links")

                        except Exception as e:
                            self._log(f"Error crawling {next_url}: {str(e)}")
                            continue

        self._log(f"Crawl completed. Total pages found: {len(pages_data)}")

        return {
            'url': url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'text_content': pages_data[0]['content']['text_content'],
            'links': list(links),
            'content_hash': pages_data[0]['content']['content_hash'],
            'screenshot_path': pages_data[0]['content']['screenshot_path'],
            'pages': pages_data,
            'crawler_logs': self._logs,
            'progress': {
                'total_pages': self.total_discovered_pages,
                'processed_pages': self.processed_pages,
                'elapsed_time': time.time() - self.start_time
            }
        }

    except Exception as e:
        error_msg = f"Failed to scrape website: {str(e)}"
        self._log(error_msg)
        raise Exception(error_msg)

    def get_logs(self):
        return self._logs

    def clear_logs(self):
        self._logs = []