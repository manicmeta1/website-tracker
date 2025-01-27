import trafilatura
from bs4 import BeautifulSoup
import requests
from typing import Dict, Any, List, Set
from urllib.parse import urlparse, urljoin
import time
import random
from screenshot_manager import ScreenshotManager

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive'
        }
        self.screenshot_manager = ScreenshotManager()
        self.visited_urls = set()
        self._logs = []
        self.session = requests.Session()
        self.retry_count = 3
        self.retry_delay = 2

    def _log(self, message: str):
        """Add a log message with timestamp"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self._logs.append(log_entry)

    def get_logs(self):
        return self._logs

    def clear_logs(self):
        self._logs = []

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

            path = parsed.path or '/'

            # Remove query parameters and fragments
            url = f"https://{netloc}{path}"
            self._log(f"Normalized URL: {url}")
            return url

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

            # Shopify-specific exclusions
            shopify_excluded = any(x in url.lower() for x in [
                '/cart', '/checkout', '/account', '/challenge',
                'login', 'logout', 'signin', 'signout'
            ])

            # File extensions to exclude
            excluded_extensions = ('.pdf', '.jpg', '.jpeg', '.png', '.gif', 
                                 '.zip', '.css', '.js', '.ico', '.woff', 
                                 '.woff2', '.svg')

            is_valid = (
                (netloc == base_domain or not netloc) and
                not url.endswith(excluded_extensions) and
                not shopify_excluded
            )

            if is_valid:
                self._log(f"Valid internal link found: {url}")
            return is_valid

        except Exception as e:
            self._log(f"Error validating URL {url}: {str(e)}")
            return False

    def _extract_links(self, soup: BeautifulSoup, base_url: str, base_domain: str) -> Set[str]:
        """Extract all valid internal links from the page"""
        links = set()
        self._log(f"Extracting links from {base_url}")

        # List of Shopify-specific selectors
        shopify_selectors = [
            'nav.navigation',
            'ul.site-nav',
            '.site-header',
            '.site-footer',
            '.collection-grid',
            '.product-card',
            '.footer-nav',
            '.menu-drawer',
            '.site-navigation'
        ]

        # Find all elements that might contain links
        for selector in shopify_selectors:
            elements = soup.select(selector)
            for element in elements:
                for a in element.find_all('a', href=True):
                    href = a.get('href', '').strip()
                    if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
                        try:
                            full_url = urljoin(base_url, href)
                            normalized_url = self._normalize_url(full_url)
                            if self._is_valid_internal_link(normalized_url, base_domain):
                                links.add(normalized_url)
                                self._log(f"Added Shopify link: {normalized_url}")
                        except Exception as e:
                            self._log(f"Error processing Shopify link {href}: {str(e)}")

        # Standard navigation elements
        nav_elements = soup.find_all(['nav', 'header', 'footer', 'ul', 'div'])
        for nav in nav_elements:
            for a in nav.find_all('a', href=True):
                href = a.get('href', '').strip()
                if href and not href.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
                    try:
                        full_url = urljoin(base_url, href)
                        normalized_url = self._normalize_url(full_url)
                        if self._is_valid_internal_link(normalized_url, base_domain):
                            links.add(normalized_url)
                            self._log(f"Added standard link: {normalized_url}")
                    except Exception as e:
                        self._log(f"Error processing standard link {href}: {str(e)}")

        self._log(f"Extracted {len(links)} valid internal links")
        for link in links:
            self._log(f"Found link: {link}")
        return links

    def _scrape_single_page(self, url: str, base_domain: str) -> Dict[str, Any]:
        """Scrape a single page with retry logic"""
        if url in self.visited_urls:
            self._log(f"Skipping already visited URL: {url}")
            return None

        self._log(f"Attempting to scrape URL: {url}")
        self.visited_urls.add(url)

        for attempt in range(self.retry_count):
            try:
                # Add random delay between requests
                if attempt > 0:
                    delay = self.retry_delay * (1 + attempt) + random.uniform(1, 3)
                    self._log(f"Retry delay: {delay} seconds")
                    time.sleep(delay)

                response = self.session.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                html_content = response.text

                # Parse HTML
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract links
                links = self._extract_links(soup, url, base_domain)
                self._log(f"Found {len(links)} internal links on page {url}")

                # Capture screenshot
                self._log("Capturing screenshot...")
                screenshot_path = self.screenshot_manager.capture_screenshot(url)
                self._log(f"Screenshot saved to: {screenshot_path}")

                # Extract text content
                self._log("Extracting text content...")
                downloaded = trafilatura.fetch_url(url)
                if not downloaded:
                    self._log("Trafilatura failed to download content, falling back to BeautifulSoup")
                    text_content = ' '.join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
                else:
                    text_content = trafilatura.extract(downloaded) or ''

                # Create content fingerprint
                content_hash = hash(text_content)

                return {
                    'url': url,
                    'timestamp': response.headers.get('Date', time.strftime('%Y-%m-%d %H:%M:%S')),
                    'html_content': html_content,
                    'text_content': text_content,
                    'links': list(links),
                    'content_hash': content_hash,
                    'screenshot_path': screenshot_path
                }

            except Exception as e:
                self._log(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt < self.retry_count - 1:
                    continue
                else:
                    self._log(f"Failed to scrape {url} after {self.retry_count} attempts")
                    return None

    def scrape_website(self, url: str, crawl_all_pages: bool = False) -> Dict[str, Any]:
        """Scrape website content with improved crawling logic"""
        try:
            self.clear_logs()
            self._log(f"Starting new crawl of {url}")
            self._log(f"Full site crawling: {'enabled' if crawl_all_pages else 'disabled'}")

            # Normalize URL and extract base domain
            url = self._normalize_url(url)
            base_domain = urlparse(url).netloc
            if base_domain.startswith('www.'):
                base_domain = base_domain[4:]
            self._log(f"Base domain: {base_domain}")

            # Initialize results
            pages_data = []
            self.visited_urls.clear()

            # Scrape initial URL
            initial_page = self._scrape_single_page(url, base_domain)
            if not initial_page:
                raise Exception(f"Failed to scrape initial page: {url}")

            pages_data.append({
                'url': url,
                'location': '/',
                'content': initial_page
            })

            if crawl_all_pages:
                urls_to_visit = set(initial_page['links'])
                self._log(f"Initially found {len(urls_to_visit)} pages to crawl")

                while urls_to_visit and len(self.visited_urls) < 100:
                    next_url = urls_to_visit.pop()
                    self._log(f"Crawling: {next_url}")

                    if next_url not in self.visited_urls:
                        time.sleep(random.uniform(2, 3))  # Polite delay
                        page_data = self._scrape_single_page(next_url, base_domain)

                        if page_data:
                            parsed_url = urlparse(next_url)
                            location = parsed_url.path if parsed_url.path else '/'

                            pages_data.append({
                                'url': next_url,
                                'location': location,
                                'content': page_data
                            })

                            # Add new links to visit
                            new_links = set(page_data['links'])
                            new_urls = new_links - self.visited_urls
                            urls_to_visit.update(new_urls)
                            self._log(f"Added {len(new_urls)} new links to crawl queue")

            self._log(f"Crawl completed. Found {len(pages_data)} pages")

            return {
                'url': url,
                'timestamp': initial_page['timestamp'],
                'text_content': initial_page['text_content'],
                'links': initial_page['links'],
                'content_hash': initial_page['content_hash'],
                'screenshot_path': initial_page['screenshot_path'],
                'pages': pages_data,
                'crawl_all_pages': crawl_all_pages,
                'crawler_logs': self._logs
            }

        except Exception as e:
            error_msg = f"Failed to scrape website: {str(e)}"
            self._log(error_msg)
            raise Exception(error_msg)